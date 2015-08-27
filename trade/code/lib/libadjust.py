import os
from download import dllib
import csv

def yAdjust(data):
	''' Adjust OHLC values using Y! provided Adj Close  '''
	mult = float(data['Adj Close']) / float(data['Close'])
	data['Open'] = float(data['Open']) * mult 
	data['High'] = float(data['High']) * mult
	data['Low'] = float(data['Low']) * mult
	data['Close'] = float(data['Close']) * mult
	data['Volume'] = int(data['Volume']) / mult

def cleanSplits(d):
	''' Convert date format and strings to floats '''
	datestr = d['DATE'].strip()
	d['DATE'] = '-'.join([ datestr[0:4], datestr[4:6], datestr[6:] ])
	if d['TYPE'] == 'DIVIDEND':
		d['VALUE'] = float(d['VALUE'])
	elif d['TYPE'] == 'SPLIT':
		denom, num = d['VALUE'].split(':')
		d['VALUE'] = float(num) / float(denom)

def getMultMap(sym):
	spath = os.path.join(dllib.SPLIT_DIR, 'divsplit_' + sym + '.csv')
	slist = list(csv.DictReader(open(spath, 'rb'), fieldnames=['TYPE', 'DATE', 'VALUE']))
	splits = filter(lambda d: d['TYPE'] in ('DIVIDEND', 'SPLIT'), slist)
	map(cleanSplits, splits)
	
	opath = os.path.join(dllib.EOD_DIR, '_' + sym + '.csv')
	ohlcv = list(csv.DictReader(open(opath, 'rb')))
	
	multmap = {}
	mults = [1]
	for splitrow in splits:
		eodrow = filter(lambda d: d['Date'] == splitrow['DATE'], ohlcv)
		if len(eodrow) == 1:
			if splitrow['TYPE'] == 'DIVIDEND':
				numerator = splitrow['VALUE']
				mults.append(1 - (numerator / float(eodrow[0]['Close'])))
			elif splitrow['TYPE'] == 'SPLIT':
				mults.append(splitrow['VALUE'])
			
			multmap[splitrow['DATE']] = reduce(lambda a, b: a * b, mults)