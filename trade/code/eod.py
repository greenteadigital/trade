import json
import const
from const import pjoin
from zipfile import ZipFile, ZIP_DEFLATED

SRC = const.ADJ_DIR

def aggregate(dpc, data):
	out = []
	start = 0
	end = dpc
	
	while end <= len(data):
		chunk = data[start:end]
		agg = {
			"Date": chunk[-1]['Date'],
			"Open": float(chunk[0]['Open']),
			"High": max(map(lambda d: float(d['High']), chunk)),
			"Low": min(map(lambda d: float(d['Low']), chunk)),
			"Close": float(chunk[-1]['Close']),
			"Volume": sum(map(lambda d: float(d['Volume']), chunk))
		}
		out.append(agg)
		
		start = end
		end = start + dpc
		
	return out
	
def getEod(params):
	symbol = params['symbol'][0]
	depth = int(params['depth'][0])
	dpc = int(params['dpc'][0])
	
	name = '_' + symbol + '.json'
	zname = name + '.zip'
	with ZipFile(pjoin(SRC, zname), 'r', ZIP_DEFLATED).open(name) as f:
		lst = json.loads(f.read())
	lst.reverse()  # flip to timeline order, oldest first
	
	if depth < len(lst):
		lst = lst[len(lst) - depth:]
	
	if dpc > 1:
		return json.dumps(aggregate(dpc, lst))
	
	elif dpc == 1:
		return json.dumps(lst)
	
