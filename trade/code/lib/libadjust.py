import const
import os
import csv
from const import pjoin
import json


def yAdjust(data):
	''' Adjust OHLC values using Y! provided Adj Close '''
	mult = float(data['Adj Close']) / float(data['Close'])
	data['Open'] = float(data['Open']) * mult 
	data['High'] = float(data['High']) * mult
	data['Low'] = float(data['Low']) * mult
	data['Close'] = float(data['Adj Close'])
	data['Volume'] = int(int(data['Volume']) / mult)
	del data['Adj Close']


def mergeAndAdjust(symbol):
	srcdir = pjoin(const.RAW_DIR, '_' + symbol)
	files = os.listdir(srcdir)
	files.sort()
	files.reverse()
	
	# Adjust hist. prices in 2 steps: first adjust the Adj Close backward to the oldest data...
	merged = []
	carried_mult = 1.0
	for f in files:
		with open(pjoin(srcdir, f), 'rb') as d:
			ld = list(csv.DictReader(d))
			if carried_mult != 1.0:
				for sess in ld:
					sess['Adj Close'] = float(sess['Adj Close']) * carried_mult
			carried_mult = float(ld[-1]['Adj Close']) / float(ld[-1]['Close'])
			merged += ld
	
	# ...and then use Adj Close to adjust the remaining values
	map(yAdjust, merged)
	
	name = '_' + symbol + '.json'
	with open(pjoin(const.ADJ_DIR, name), 'wb') as out:
		out.write(json.dumps(merged))
	print name

if __name__ == '__main__':
	for sym in os.listdir(const.RAW_DIR):
		mergeAndAdjust(sym[1:])
		'''
_OFLX.json
_OFS.json
_OGCP.json
_OGE.json
_OGEN.json
_OGS.json
_OGXI.json
_OHAI.json
Traceback (most recent call last):
  File "C:\Users\Ben\eclipse-workspace\trade\code\lib\libadjust.py", line 47, in <module>
    mergeAndAdjust(sym[1:])
  File "C:\Users\Ben\eclipse-workspace\trade\code\lib\libadjust.py", line 38, in mergeAndAdjust
    map(yAdjust, merged)
  File "C:\Users\Ben\eclipse-workspace\trade\code\lib\libadjust.py", line 10, in yAdjust
    mult = float(data['Adj Close']) / float(data['Close'])
ZeroDivisionError: float division by zero

		'''
