import const
import os
import csv
from const import pjoin, strio, pexists
import json
import sys
from zipfile import ZipFile, ZIP_DEFLATED

def yAdjust(data):
	''' Adjust OHLC values using Y! provided Adj Close '''

	try:
		mult = float(data['Adj Close'].replace('null', '0')) / float(data['Close'].replace('null', '0'))
		data['Open'] = float(data['Open'].replace('null', '0')) * mult 
		data['High'] = float(data['High'].replace('null', '0')) * mult
		data['Low'] = float(data['Low'].replace('null', '0')) * mult
		data['Close'] = float(data['Adj Close'].replace('null', '0'))
		data['Volume'] = int(int(data['Volume'].replace('null', '0')) / mult)
		del data['Adj Close']
	except ZeroDivisionError:
		pass
	except AttributeError as e:
		print data
		raise e

def mergeAndAdjust(symbol):
	''' Merge raw csv data files and apply adjusted close '''
	
	path = pjoin(const.RAW_DIR, '_' + symbol + '.csv.zip')
	if pexists(path):
		with ZipFile(path, 'r', ZIP_DEFLATED) as _zip:
			files = _zip.namelist() 
			files.sort()
		
			# Adjust hist. prices in 2 steps: first adjust the Adj Close backward to the oldest data...
			merged = []
			carried_mult = 1.0
			for f in files:
				ld = list(csv.DictReader(strio(_zip.read(f))))
				if ld:
					ld.sort(key = lambda d: d['Date']) # oldest first
					for d in ld:
						if len(merged) > 0:
#							 print 'Tail:', merged[-1]['Date'] + ';', 'Incoming', files[n] + ':', d['Date']
							## Fix overlapping days in raw files
							while len(merged) > 0 and merged[-1]['Date'] >= d['Date']:
								merged.pop()
							merged += [d]
						else:
							merged += [d]
					
					if carried_mult != 1.0:
						for sess in merged:
							if sess['Adj Close'] == 'null':
								sess['Adj Close'] = 0
							sess['Adj Close'] = str(float(sess['Adj Close']) * carried_mult)
					try:
						carried_mult = float(merged[-1]['Adj Close']) / float(merged[-1]['Close'])
					except ZeroDivisionError:
						pass
		
			# ...and then use Adj Close to adjust the remaining values
			merged.sort(key = lambda d: d['Date'])
			merged.reverse()	# to newest first
			map(yAdjust, merged)
		
			name = '_' + symbol + '.json'
			zname = name + '.zip'
			with ZipFile(pjoin(const.ADJ_DIR, zname), 'w', ZIP_DEFLATED) as out:
				out.writestr(name, json.dumps(merged))
			print zname

if __name__ == '__main__':
	syms = map(lambda n: n.split('.')[0].lstrip('_'), os.listdir(const.RAW_DIR))
	syms.sort()
	for sym in syms:
		mergeAndAdjust(sym)
	pass

