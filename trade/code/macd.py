import csv
import json
from lib.libadjust import yAdjust
import const

SRC = const.RAW_DIR

def aggregate(dpc, data):
	out = []
	start = 0
	end = dpc
	
	while end <= len(data):
		chunk = data[start : end]
		agg = {
			"Date": chunk[-1]['Date'],
			"Close": float(chunk[-1]['Close']),
			}
		out.append(agg);
		
		start = end;
		end = start + dpc;
	
	return out

def calcMacd(**kwargs):
	data = kwargs['data']
	
	fast_emas = []
	end = int(kwargs['fast'])
	fast_smoothing = 2.0 / (end + 1)
	sub = data[:end]
	last_fast = sum(map(lambda d: float(d['Close']), sub)) / end
	for eod in data[end:]:
		ema = (float(eod['Close']) - last_fast) * fast_smoothing + last_fast
		d = {eod['Date'] : ema}
		fast_emas.append(d)
		last_fast = ema
	
	slow_emas = []
	end = int(kwargs['slow'])
	slow_smoothing = 2.0 / (end + 1)
	sub = data[:end]
	last_slow = sum(map(lambda d: float(d['Close']), sub)) / end
	for eod in data[end:]:
		ema = (float(eod['Close']) - last_slow) * slow_smoothing + last_slow
		d = {eod['Date'] : ema}
		slow_emas.append(d)
		last_slow = ema
	
	fast_emas = fast_emas[len(fast_emas) - len(slow_emas):]
	
	def merge(tup):
		assert tup[0].keys()[0] == tup[1].keys()[0]
		return {tup[0].keys()[0] : tup[0].values()[0] - tup[1].values()[0]}
	
	macds = map(merge, zip(fast_emas, slow_emas))
	
	signal = []
	end = int(kwargs['signal'])
	sig_smoothing = 2.0 / (end + 1)
	sub = macds[:end]
	last_sig = sum(map(lambda n: n.values()[0], sub)) / end
	for macd in macds[end:]:
		ema = (macd.values()[0] - last_sig) * sig_smoothing + last_sig
		signal.append(ema)
		last_sig = ema
	
	macds = macds[len(macds) - len(signal):]
	
	def reshuffle(li):
		out = {}
		out['Date'] = li[0].keys()[0]
		out['MACD'] = li[0].values()[0]
		out['Sig'] = li[1]
		out['d'] = abs(out['MACD'] - out['Sig']) 
		return out
	
	return map(reshuffle, zip(macds, signal))

def getMacd(params):
	symbol = params['symbol'][0]
	fast = int(params['fast'][0])
	slow = int(params['slow'][0])
	signal = int(params['signal'][0])
	depth = int(params['depth'][0])
	dpc = int(params['dpc'][0])
	
	lst = list(csv.DictReader(open(SRC + r"\_" + symbol + ".csv", 'rb')))
	lst.reverse()  # reverse rows to be in timeline (earliest -> most) recent order
	
	fdepth = depth + ((slow + signal) * dpc) 
	if fdepth < len(lst):
		lst = lst[len(lst) - fdepth:]
	
	map(yAdjust, lst)
	
	rows = []
	for row in lst:
		rows.append({'Date':row['Date'], 'Close':row['Close']})
	
	if dpc > 1:
		data = aggregate(dpc, rows)
	elif dpc == 1:
		data = rows
	
	return json.dumps(calcMacd(fast=fast, slow=slow, signal=signal, data=data))


