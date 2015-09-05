import json
import os
import const
from const import pjoin, pexists, pisfile
from zipfile import ZipFile, ZIP_DEFLATED
import multiprocessing as multi

SRC = const.ADJ_DIR
pool = multi.Pool(3)

def numLines(symbol):
	_zip = ZipFile(pjoin(SRC, "_" + symbol + '.json.zip'), 'r', ZIP_DEFLATED)
	with _zip.open("_" + symbol + '.json', 'r') as f:
		for count, unused in enumerate(json.load(f), 1):
			pass
	return count

def getHistory(*args):
	hfile = pjoin(const.JSON_DIR, "history.json")
	
	# Set the file's [a|m]time back to epoch to force rewrite of hfile.
	os.utime(hfile, (0, 0))
	
	base = os.path.getmtime(hfile)
	newer = filter(lambda f: os.path.getmtime(os.path.join(SRC, f)) > base, os.listdir(SRC))
	
	if newer:
		hist = json.load(open(hfile, 'rb'))  # = [ {"A": 999}, {"Z": 234}, {"MM": 777} ... ]
		
		count = 0
		def updateHist(count):
			map(lambda d: d.update((k, count) for k, unused in d.items() if k == symbol), hist)
			count += 1
		
		for symbol in map(lambda f: f.split('.')[0][1:], newer):
			print 'recalculating history for', symbol
# 			count = numLines(ZipFile(pjoin(SRC, "_" + symbol + '.json.zip'), 'r', ZIP_DEFLATED)) - 1
			pool.apply_async(numLines, [symbol], callback=updateHist)
			
			
		while 1:
			if count == len(newer):
				update = json.dumps(map(lambda t: dict(t), sorted(hist, key=lambda x: x.values()[0], reverse=True)))
				open(hfile, 'wb').write(update)
				return update
			else:
# 				print count
				continue
	
	else:
		return open(hfile, 'rb').read()

# if __name__ == '__main__':
# 	pass