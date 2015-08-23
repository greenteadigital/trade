import csv
from download import dllib
import os
import sys

def cleanSplits(d):
	datestr = d['DATE'].strip()
	d['DATE'] = '-'.join([ datestr[0:4], datestr[4:6], datestr[6:] ])
	if d['TYPE'] == 'DIVIDEND':
		d['VALUE'] = float(d['VALUE'])
	elif d['TYPE'] == 'SPLIT':
		denom, num = d['VALUE'].split(':')
		d['VALUE'] = float(num) / float(denom) 

for f in os.listdir(dllib.SPLIT_DIR):
	print f
	spath = os.path.join(dllib.SPLIT_DIR, f)
	slist = list(csv.DictReader(open(spath, 'rb'), fieldnames=['TYPE', 'DATE', 'VALUE']))
	splits = filter(lambda d: d['TYPE'] in ('DIVIDEND', 'SPLIT'), slist)
	map(cleanSplits, splits)
	
	opath = os.path.join(dllib.EOD_DIR, f.replace('divsplit', ''))
	ohlcv = list(csv.DictReader(open(opath, 'rb')))
	
	multmap = {}
	mults = []
	for splitrow in splits:
		eodrow = filter(lambda d: d['Date'] == splitrow['DATE'], ohlcv)
		if len(eodrow) == 1:
			if splitrow['TYPE'] == 'DIVIDEND':
				mults.append(1 - (splitrow['VALUE'] / float(eodrow[0]['Close'])))
			elif splitrow['TYPE'] == 'SPLIT':
				mults.append(splitrow['VALUE'])
			
			multmap[splitrow['DATE']] = reduce(lambda a, b: a * b, mults)
			
	for m in sorted(multmap):
		print m, multmap[m]
	sys.exit()
