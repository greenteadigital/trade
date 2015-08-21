import sqlite3
import dllib
import os
import csv
import sys
import urllib2
from cStringIO import StringIO as strio

print dllib.CSV_DIR
print dllib.DB_DIR
print dllib.FTP_DIR
sys.exit()

# build URLs with symbols and intended date range
# make requests to yahoo in round-robin fashion
def downloadEodData():
	ip2host = dllib.getIpMap()
	ips = ip2host.keys()
	ips_curr_idx = 0
	ips_max_idx = len(ips) - 1
	symconn = sqlite3.connect(os.path.join(dllib.DB_DIR, "symbols.db"))
	symcurs = symconn.cursor()
	eodconn = sqlite3.connect(os.path.join(dllib.DB_DIR, "eod_data.db"))
	eodcurs = eodconn.cursor()
	symselect = "select SYMBOL from nasdaqlisted union select NASDAQ_SYMBOL from otherlisted"
	db_syms = map(lambda t: '_' + t[0], symcurs.execute(symselect).fetchall())
	fs_syms = map(lambda n: n.split('.')[0], os.listdir(dllib.CSV_DIR))
	syms = filter(lambda i: i.isalpha(), map(lambda i: i.lstrip('_'), list(set(db_syms) - set(fs_syms))))
	for symbol in syms:
		print symbol
		ip = ips[ips_curr_idx]
		params = (ip, symbol)
		url = "http://%s/table.csv?s=%s&a=0&b=1&c=1900&d=12&e=31&f=2099&g=d&ignore=.csv" % params 
		loc = urllib2.Request(url)
		loc.add_header('Accept-Encoding', 'gzip, deflate')
		loc.add_header('Host', ip2host[ip])
		opener = urllib2.build_opener()
		print 'requesting', url
		try:
			csv_txt = dllib.tryDecompress(opener.open(loc).read())
			out = open(os.path.join(dllib.CSV_DIR, '_' + symbol + '.csv'), 'wb')
		except urllib2.HTTPError as err:
			sys.stderr.write(str(err))
			sys.stderr.flush()
			if ips_curr_idx < ips_max_idx:
				ips_curr_idx += 1
			else:
				ips_curr_idx = 0
			continue
		out.write(csv_txt)
		out.close()
		print 'saved', '_' + symbol + '.csv'
		if ips_curr_idx < ips_max_idx:
			ips_curr_idx += 1
		else:
			ips_curr_idx = 0
		reader = csv.DictReader(strio(csv_txt))
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
		for unused in xrange(len(row.keys())):
			qlst.append('?')
		qms = ','.join(qlst)
		ins = 'insert into _%s (DATE,OPEN,HIGH,LOW,CLOSE,VOLUME,ADJ_CLOSE) values (%s)' % (params[0], qms)
		print ins
		eodcurs.executemany(ins, vals)
		eodconn.commit()

dllib.backupSymbols()
dllib.downloadSymbols()
dllib.reloadSymbols()
downloadEodData()


# EOF
