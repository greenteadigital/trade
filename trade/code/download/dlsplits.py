import dllib
import os
import urllib2
import sqlite3
import csv
import const
from cStringIO import StringIO as strio

def loadSplitData(csv_str, symbol):
	splitconn = sqlite3.connect(os.path.join(dllib.DB_DIR, "div_splits.db"))
	splitcurs = splitconn.cursor()
	cols = ['TYPE', 'DATE', 'VALUE']
	params = (symbol, ','.join(cols))
	splitcurs.execute("drop table if exists ds_%s" % params[0])
	create = "create table ds_%s (%s)" % params
	print create
	splitcurs.execute(create)
	reader = list(csv.DictReader(strio(csv_str), fieldnames=cols))
	data = filter(lambda d: d['TYPE'] in ('DIVIDEND', 'SPLIT'), reader)
	
	vals = [(
			row['TYPE'][0:3],
			'-'.join([ row['DATE'].strip()[0:4], row['DATE'].strip()[4:6], row['DATE'].strip()[6:] ]),
			row['VALUE']) for row in data]
	qlst = []
	for unused in xrange(len(cols)):
		qlst.append('?')
	qms = ','.join(qlst)
	ins = 'insert into ds_%s (TYPE,DATE,VALUE) values (%s)' % (params[0], qms)
	print ins
	splitcurs.executemany(ins, vals)
	splitconn.commit()
	print

def downloadSplitData():
	ip2host = dllib.getIpMap()
	syms = map(lambda n: n.lstrip('_').split('.')[0], os.listdir(dllib.EOD_DIR))
	for symbol in syms:
		ip2host = dllib.getIpMap()
		success = False
		for ip in ip2host:
			params = (ip, symbol)
			url = "http://%s/x?s=%s&a=0&b=1&c=1900&d=11&e=31&f=2099&g=v&y=0&z=99999" % params
			loc = urllib2.Request(url)
			loc.add_header('Accept-Encoding', 'gzip, deflate')
			loc.add_header('Host', ip2host[ip])
			opener = urllib2.build_opener()
			print 'requesting', url
			try:
				csv_txt = dllib.tryDecompress(opener.open(loc).read())
				open(os.path.join(const.SPLIT_DIR, 'divsplit_' + symbol + '.csv'), 'wb').write(csv_txt)
				success = True
				break
			except urllib2.HTTPError:
				continue
		if success:
			print 'success', symbol
			loadSplitData(csv_txt, symbol)
		else:
			print 'FAIL', symbol
			
# downloadSplitData()

