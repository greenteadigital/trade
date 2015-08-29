import json
import os
import const

SRC = const.RAW_DIR

def numLines(fname):
	with open(fname) as f:
		for count, unused in enumerate(f, 1):
			pass
	return count

def getHistory(*args):
	hfile = r".\data\json\history.json"
	
	# Set the file's [a|m]time back to epoch to force rewrite of hfile.
	# os.utime(hfile, (0,0))
	
	base = os.path.getmtime(hfile)
	newer = filter(lambda f: os.path.getmtime(os.path.join(SRC, f)) > base, os.listdir(SRC))
	
	if newer:
		hist = json.load(open(hfile, 'rb'))  # = [ {"A": 999}, {"Z": 234}, {"MM": 777} ... ]
		
		for symbol in map(lambda f: f.split('.')[0][1:], newer):
			count = numLines(os.path.join(SRC, "_" + symbol + '.csv')) - 1
			map(lambda d: d.update((k, count) for k, v in d.items() if k == symbol), hist)
		
		update = json.dumps(map(lambda t: dict(t), sorted(hist, key=lambda x: x.values()[0], reverse=True)))
		open(hfile, 'wb').write(update)
		return update
	
	else:
		return open(hfile, 'rb').read()
