import os
import json
from const import RAW_DIR, JSON_DIR, pjoin

def numLines(fname):
	with open(fname) as f:
		for count, unused in enumerate(f, 1):
			pass
	return count

def getSyms(params):
	if params:
		order = params['order'][0]
		
		if order == 'aplha':
			symbols = map(lambda f: f.split('.')[0].lstrip('_'), os.listdir(RAW_DIR))
		
		elif order == 'biggest':
			hfile = pjoin(JSON_DIR, "history.json")
			hist = json.load(open(hfile, 'rb'))
			symbols = map(lambda m: m.keys()[0] , sorted(hist, key=lambda x: x.values()[0], reverse=True))
	
		return json.dumps(symbols)
	
	else:
		return map(lambda f: f.split('.')[0].lstrip('_'), os.listdir(RAW_DIR))
	
