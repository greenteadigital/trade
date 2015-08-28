import os
from download import dllib
import csv
import symbols
from const import SPLIT_DIR, RAW_DIR

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
	datestr = d['SplitDate'].strip()
	d['SplitDate'] = '-'.join([ datestr[0:4], datestr[4:6], datestr[6:] ])
	if d['SplitType'] == 'DIVIDEND':
		d['SplitValue'] = float(d['SplitValue'])
	elif d['SplitType'] == 'SPLIT':
		denom, num = d['SplitValue'].split(':')
		d['SplitValue'] = float(num) / float(denom)

def getMultMap(sym):
	spath = os.path.join(SPLIT_DIR, 'divsplit_' + sym + '.csv')
	slist = list(csv.DictReader(open(spath, 'rb'), fieldnames=['SplitType', 'SplitDate', 'SplitValue']))
	splits = filter(lambda d: d['SplitType'] in ('DIVIDEND', 'SPLIT'), slist)
	map(cleanSplits, splits)
	
	opath = os.path.join(RAW_DIR, '_' + sym + '.csv')
	ohlcv = list(csv.DictReader(open(opath, 'rb')))
	
	multmap = {}
	mults = [1]
	for splitrow in splits:
		# # TODO: Handle case where symbols has never had a split event
		eodrow = filter(lambda d: d['Date'] == splitrow['SplitDate'], ohlcv)
		if len(eodrow) == 1:
			if splitrow['SplitType'] == 'DIVIDEND':
				numerator = splitrow['SplitValue']
				mults.append(1 - (numerator / float(eodrow[0]['Close'])))
			elif splitrow['SplitType'] == 'SPLIT':
				mults.append(splitrow['SplitValue'])
			
			multmap[splitrow['SplitDate']] = reduce(lambda a, b: a * b, mults)
	return multmap

if __name__ == "__main__":
	for sym in symbols.getSyms(None):
		print sym
		for k, v in getMultMap(sym).items():
			print k, v
