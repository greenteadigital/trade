import socket
from ftplib import FTP
import sqlite3
import os
import csv
import urllib2
import sys
import zlib
from cStringIO import StringIO as strio

PROJ_DIR = r'C:\Users\Ben\eclipse-workspace\Trading\web'
FTP_DIR = os.path.join(PROJ_DIR, r'data\ftp')
DB_DIR = os.path.join(PROJ_DIR, r'data\sqlite')
CSV_DIR = os.path.join(PROJ_DIR, r'data\csv')

FIN_STATUS = {
'D':'Deficient: Issuer Failed to Meet NASDAQ Continued Listing Requirements',
'E':'Delinquent: Issuer Missed Regulatory Filing Deadline',
'Q':'Bankrupt: Issuer Has Filed for Bankruptcy',
'N':'Normal (Default): Issuer Is NOT Deficient, Delinquent, or Bankrupt.',
'G':'Deficient and Bankrupt',
'H':'Deficient and Delinquent',
'J':'Delinquent and Bankrupt',
'K':'Deficient, Delinquent, and Bankrupt'
}

def backupSymbols():
	for f in filter(lambda n: n.endswith('.bak'), os.listdir(FTP_DIR)):
		os.remove(os.path.join(FTP_DIR, f))
	for f in filter(lambda n: n.endswith('.txt'), os.listdir(FTP_DIR)):
			os.rename(os.path.join(FTP_DIR, f), os.path.join(FTP_DIR, f + '.bak'))

def downloadSymbols():
	backupSymbols()
	files = ('nasdaqlisted.txt', 'otherlisted.txt')
	ftp = FTP('ftp.nasdaqtrader.com')
	ftp.login()
	ftp.cwd("SymbolDirectory")
	for f in files:
		mtime = ftp.sendcmd('MDTM ' + f).split()[1]
		name = f.split('.')[0] + '_' + mtime + '.txt'
		out = open(os.path.join(FTP_DIR, name),'wb')
		ftp.retrbinary("RETR %s" % f, out.write)
		out.close()
	ftp.quit()

# TODO: load symbols and metadata into sqlite
def loadSymbols():
	downloadSymbols()
	#see http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs
	with sqlite3.connect(os.path.join(DB_DIR, "symbols.db")) as conn:
		curs = conn.cursor()
		curs.execute("drop table if exists financial_status")
		create_status = "create table financial_status (CODE, DESCRIPTION)"
		print create_status
		curs.execute(create_status)
		for item in FIN_STATUS:
			curs.execute("insert into financial_status (CODE, DESCRIPTION) values (?,?)", (item, FIN_STATUS[item]))
		conn.commit()
		for f in filter(lambda n: n.endswith('.txt'), os.listdir(FTP_DIR)):
			with open(os.path.join(FTP_DIR, f),'rb') as csvfile:
				reader = csv.DictReader(csvfile, delimiter="|")
				for row in reader:
					tables = ('nasdaqlisted', 'otherlisted')
					if f.split('_')[0] in tables:
						cols = map(lambda s: s.replace(' ','_').upper(), sorted(row.keys()))
						params = (f.split('_')[0], ','.join(cols))
						curs.execute("drop table if exists %s" % params[0])
						create = "create table %s (%s)" % params
						print create
						curs.execute(create)
						break
				for row in reader:
					qlst = []
					for n in xrange(len(row.keys())):
						qlst.append('?')
					qms = ','.join(qlst)
					ins = 'insert into %s (%s) values (%s)' % (params[0], params[1], qms)
					curs.execute(ins, ([str(row[key]) for key in sorted(row.keys())]))
				conn.commit()
		for table in tables:
			last = 'select * from %s where rowid=%s' % (table ,curs.execute('select max(rowid) from %s' % table).fetchone()[0])

def getIpMap():
	hosts = ('real-chart.finance.yahoo.com', 'ichart.finance.yahoo.com')
	ip2host = {}
	for host in hosts:
		ips = socket.gethostbyname_ex(host)[2]
		for ip in ips:
			ip2host[ip] = host
	return ip2host

def tryDecompress(response):
	'''For decompressing a gzipped http server response using zlib'''
	magicNum = "\x1f\x8b\x08"
	magicOffset = response.find(magicNum)
	#magicCount = response.count(magicNum)
	if magicOffset > -1:
		try:
			# Ignore the 10-byte gzip file header and try to decompress the rest
			return zlib.decompress(response[magicOffset+10:], -15)
		except zlib.error as e:
			raise e
	else:
		return response

# TODO: build URLs with symbols and intended date range
# TODO: make requests to yahoo in round-robin fashion
def downloadEodData():
	loadSymbols()
	ip2host = getIpMap()
	ips = ip2host.keys()
	ips_curr_idx = 0
	ips_max_idx = len(ips) - 1
	symconn = sqlite3.connect(os.path.join(DB_DIR, "symbols.db"))
	symcurs = symconn.cursor()
	eodconn = sqlite3.connect(os.path.join(DB_DIR, "eod_data.db"))
	eodcurs = eodconn.cursor()
	symselect = "select SYMBOL from nasdaqlisted union select NASDAQ_SYMBOL from otherlisted"
	db_syms = map(lambda t: '_' + t[0], symcurs.execute(symselect).fetchall())
	fs_syms = map(lambda n: n.split('.')[0], os.listdir(CSV_DIR))
	syms = filter(lambda i: i.isalpha(), map(lambda i: i.lstrip('_'), list(set(db_syms) - set(fs_syms))))
	for symbol in syms:
		print symbol
		ip = ips[ips_curr_idx]
		params = (ip, symbol)
		url="http://%s/table.csv?s=%s&d=12&e=31&f=2099&g=d&a=1&b=1&c=1900&ignore=.csv" % params 
		loc = urllib2.Request(url)
		loc.add_header('Accept-Encoding', 'gzip, deflate')
		loc.add_header('Host', ip2host[ip])
		opener = urllib2.build_opener()
		print 'requesting', url
		try:
			csv_txt = tryDecompress(opener.open(loc).read())
			out = open(os.path.join(CSV_DIR, '_' + symbol + '.csv'), 'wb')
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
			cols = map(lambda s: s.replace(' ','_').upper(), sorted(row.keys()))
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
		for n in xrange(len(row.keys())):
			qlst.append('?')
		qms = ','.join(qlst)
		ins = 'insert into _%s (DATE,OPEN,HIGH,LOW,CLOSE,VOLUME,ADJ_CLOSE) values (%s)' % (params[0], qms)
		print ins
		eodcurs.executemany(ins, vals)
		eodconn.commit()

downloadEodData()


#EOF