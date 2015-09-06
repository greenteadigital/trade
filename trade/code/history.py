import json
import os
import const
from const import pjoin
from zipfile import ZipFile, ZIP_DEFLATED

SRC = const.ADJ_DIR

def numLines(symbol):
	name = "_" + symbol + '.json'
	zname = name + '.zip'
	_zip = ZipFile(pjoin(SRC, zname), 'r', ZIP_DEFLATED)
	with _zip.open(name, 'r') as f:
		for count, unused in enumerate(json.load(f), 1):
			pass
	return (symbol, count)

def getHistory(*args):
	pool = args[0]['pool']
	histpath = pjoin(const.JSON_DIR, "history.json")
	
# 	Set the file's [a|m]time back to epoch to force rewrite of histpath.
# 	os.utime(histpath, (0, 0))
	
	base = os.path.getmtime(histpath)
	newer = filter(lambda f: os.path.getmtime(os.path.join(SRC, f)) > base, os.listdir(SRC))
	
	with open(histpath, 'rb') as hfile:
		if newer:
			hist = []
			
			def updateHist(tup):
				hist.append({tup[0] : tup[1]})
			
			for symbol in map(lambda f: f.split('.')[0][1:], newer):
				pool.apply_async(numLines, [symbol], callback=updateHist)

			while 1:
				if len(hist) < len(newer):
					continue
				else:
					pool.close()
					update = json.dumps(map(lambda t: dict(t), sorted(hist, key=lambda x: x.values()[0], reverse=True)))
					open(histpath, 'wb').write(update)
					return update
		else:
			pool.close()
			return hfile.read()
