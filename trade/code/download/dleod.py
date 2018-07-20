import sqlite3
import dllib
import os
import csv
import urllib2
from cStringIO import StringIO as strio
import const

def loadEodData(csv_str, symbol):
	eodconn = sqlite3.connect(os.path.join(dllib.DB_DIR, "div_splits.db"))
	eodcurs = eodconn.cursor()
	reader = csv.DictReader(strio(csv_str))
	
	for row in reader:
		cols = map(lambda s: s.replace(' ', '_').upper(), sorted(row.keys()))
		params = (symbol, ','.join(cols))
		eodcurs.execute("drop table if exists _%s" % params[0])
		create = "create table _%s (%s)" % params
		print create
		eodcurs.execute(create)
		break
	
	vals = [(
			row['Date'],
			row['Open'],
			row['High'],
			row['Low'],
			row['Close'],
			row['Volume'],
			row['Adj Close']) for row in reader]
	qlst = []
	for unused in xrange(len(vals[0])):
		qlst.append('?')
	qms = ','.join(qlst)
	ins = 'insert into _%s (DATE,OPEN,HIGH,LOW,CLOSE,VOLUME,ADJ_CLOSE) values (%s)' % (params[0], qms)
	print ins
	eodcurs.executemany(ins, vals)
	eodconn.commit()
	print

# build URLs with symbols and intended date range
# make requests to 'oohay'.reverse() in round-robin fashion
def downloadEodData():
	symconn = sqlite3.connect(os.path.join(dllib.DB_DIR, "symbols.db"))
	symcurs = symconn.cursor()
	symselect = "select SYMBOL from nasdaqlisted union select NASDAQ_SYMBOL from otherlisted"
	db_syms = map(lambda t: '_' + t[0], symcurs.execute(symselect).fetchall())
	fs_syms = map(lambda n: n.split('.')[0], os.listdir(const.RAW_DIR))
	syms = filter(lambda i: i.isalpha(), map(lambda i: i.lstrip('_'), list(set(db_syms) - set(fs_syms))))
	for symbol in syms:
		ip2host = dllib.getIpMap()
		success = False
		for ip in ip2host:
			params = (ip, symbol)
			url = "http://%s/table.csv?s=%s&a=0&b=1&c=1900&d=11&e=31&f=2099&g=d" % params 
			loc = urllib2.Request(url)
			loc.add_header('Accept-Encoding', 'gzip, deflate')
			loc.add_header('Host', ip2host[ip])
			opener = urllib2.build_opener()
			print 'requesting', url
			try:
				csv_txt = dllib.tryDecompress(opener.open(loc).read())
				open(os.path.join(const.RAW_DIR, '_' + symbol + '.csv'), 'wb').write(csv_txt)
				success = True
				break
			except urllib2.HTTPError:
				continue
		if success:
			print 'success', symbol
			loadEodData(csv_txt, symbol)
		else:
			print 'FAIL', symbol
		

dllib.backupSymbols()
dllib.downloadSymbols()
dllib.reloadSymbols()
downloadEodData()


# EOF
