import csv
import json

SRC = r".\data\csv"

def getObv(params):
	symbol = params['symbol'][0]
	dpc = int(params['dpc'][0])
	
	def aggregate(data):
		out = []
		start = dpc
		end = start + dpc
		
		while end <= len(data):
			chunk = data[start : end]	# ascending (timeline) order
			
			agg = { "Date" : chunk[-1]['Date'] }
			
			if float(chunk[-1]['Close']) > float(data[start - 1]['Close']):
				
				if len(out) > 0:
					agg["OBV"] = out[-1]['OBV'] + sum(map(lambda d: int(d['Volume']), chunk))
					
				else:
					agg["OBV"] = sum(map(lambda d: int(d['Volume']), chunk))
					
			elif float(chunk[-1]['Close']) < float(data[start - 1]['Close']):
				
				if len(out) > 0:
					agg["OBV"] = out[-1]['OBV'] - sum(map(lambda d: int(d['Volume']), chunk))
					
				else:
					agg["OBV"] = -1 * sum(map(lambda d: int(d['Volume']), chunk))
			
			elif float(chunk[-1]['Close']) == float(data[start - 1]['Close']):
				
				if len(out) > 0:
					agg["OBV"] = out[-1]['OBV']
					
				else:
					agg["OBV"] = 0

			out.append(agg);
			start = end;
			end = start + dpc;
		
		return out
	
	l = list(csv.DictReader(open(SRC + r"\_" + symbol + ".csv", 'rb')))
	l = l[:len(l) - (len(l) % dpc)]
	l.reverse()
	return json.dumps(aggregate(l))