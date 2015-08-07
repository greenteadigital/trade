import csv
import json

SRC = r".\data\csv"

def getMacd(params):
	symbol = params['symbol'][0]
	fast = int(params['fast'][0])
	slow = int(params['slow'][0])
	signal = int(params['signal'][0])
	dpc = int(params['dpc'][0])
	
	def aggregate(data):
		if (dpc > 1):
			out = []
			start = 0
			end = dpc
			
			while end < len(data):
				chunk = data[start : end]
				agg = {
					"Date": chunk[0]['Date'],
					"Close": float(chunk[0]['Close']),
					}
				out.append(agg);
				
				start = end;
				end = start + dpc;
			
			return out
		else:
			return data
	
	rows = []
	for row in csv.DictReader(open(SRC + r"\_" + symbol + ".csv", 'rb')):
		rows.append({'Date':row['Date'], 'Close':row['Close']})
	rows = aggregate(rows)
	rows.reverse()	## reverse rows to be in earliest -> most recent order
	
	def macd(**kwargs):
		
		fast_emas = []
		end = int(kwargs['fast'])
		fast_smoothing = 2.0 / (end + 1)
		sub = rows[:end]
		last_fast = sum(map(lambda d: float(d['Close']), sub)) / end
		for eod in rows[end:]:
			ema = (float(eod['Close']) - last_fast) * fast_smoothing + last_fast
			d = {eod['Date'] : ema}
			fast_emas.append(d)
			last_fast = ema
		
		slow_emas = []
		end = int(kwargs['slow'])
		slow_smoothing = 2.0 / (end + 1)
		sub = rows[:end]
		last_slow = sum(map(lambda d: float(d['Close']), sub)) / end
		for eod in rows[end:]:
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
		
		return json.dumps(map(reshuffle, zip(macds, signal)))
			
	return macd(fast=fast, slow=slow, signal=signal)


