import csv
import json
import os
from setuptools.command.easy_install import update_dist_caches

SRC = r".\data\csv"

def getHistory(*args):
	hfile = r".\data\json\history.json"
	base = os.path.getmtime(hfile)
	newer = filter(lambda f: os.path.getmtime(os.path.join(SRC, f)) > base, os.listdir(SRC))
	
	if newer:
		hist = json.load(open(hfile,'rb'))
		for f in map(lambda f: f.split('.')[0][1:], newer):
			hist[f] = len(open(os.path.join(SRC, "_" + f + '.csv'), 'rb').readlines()) - 1
		update = json.dumps(hist)
		open(hfile,'wb').write(update)
		return update
	else:
		return open(hfile, 'rb').read()
