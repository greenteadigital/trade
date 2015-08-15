import csv
import json

SRC = r".\data\csv"

def getObv(params):
	
	lst = list(csv.DictReader(open(SRC + r"\_" + params['symbol'][0] + ".csv", 'rb')))
	lst.reverse()
	out = []
	
	firstClose = float(lst[0]['Close'])
	lst = lst[1:]
	
	for n in xrange(len(lst)):
		
		obv = { 'Date' : lst[n]['Date'] }
		
		thisClose = float(lst[n]['Close'])
		lastClose = float(lst[n-1]['Close'])
		
		if out:
			if thisClose > lastClose:
				obv['OBV'] = out[-1]['OBV'] + int(lst[n]['Volume'])
			
			elif thisClose < lastClose:
				obv['OBV'] = out[-1]['OBV'] - int(lst[n]['Volume'])
			
			else:
				obv['OBV'] = out[-1]['OBV']
		
		else:
			if thisClose > firstClose:
				obv['OBV'] = int(lst[n]['Volume'])
			
			elif thisClose < firstClose:
				obv['OBV'] = int(lst[n]['Volume']) * -1
			
			else:
				obv['OBV'] = 0
		
		out.append(obv)
	
	return json.dumps(out)
	
	
	
	
	
	
	
	
	
	
	
	
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
