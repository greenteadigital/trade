import os, json
dir_ = r".\data\csv"

def numLines(fname):
	with open(fname) as f:
		for count, unused in enumerate(f, 1):
			pass
	return count

def getSyms(params):
	order = params['order'][0]
	
	if order == 'aplha':
		symbols = map(lambda f: f.split('.')[0].lstrip('_'), os.listdir(dir_))
		
	elif order == 'biggest':
		hfile = r".\data\json\history.json"
		hist = json.load(open(hfile, 'rb'))
		symbols = map(lambda m: m.keys()[0] , sorted(hist, key=lambda x: x.values()[0], reverse=True))
	
	return json.dumps(symbols)
