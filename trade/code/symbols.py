import os, json
dir_ = r".\data\csv"

def numLines(fname):
    with open(fname) as f:
        for count, line in enumerate(f, 1):
            pass
    return count

def getSyms(params):
	order = params['order'][0]
	
	if order == 'aplha':
		symbols = map(lambda f: f.split('.')[0].lstrip('_'), os.listdir(dir_))
		return json.dumps(symbols)
		
	elif order == 'biggest':
		hfile = r".\data\json\history.json"
		hist = json.load(open(hfile,'rb'))
		return json.dumps(map(lambda map: map.keys()[0] , sorted(hist, key=lambda x: x.values()[0], reverse=True)))
