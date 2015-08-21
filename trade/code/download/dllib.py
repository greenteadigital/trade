import socket
from ftplib import FTP
import sqlite3
import os
import csv
import zlib

PROJ_DIR = os.path.join(os.environ['HOME'], r'eclipse-workspace\trade')
FTP_DIR = os.path.join(PROJ_DIR, r'data\ftp')
DB_DIR = os.path.join(PROJ_DIR, r'data\sqlite')
EOD_DIR = os.path.join(PROJ_DIR, r'data\eod-csv')
SPLIT_DIR = os.path.join(PROJ_DIR, r'data\divs-splits')

def backupSymbols():
	''' Backup current symbol files and download latest symbols from nasdaq ftp '''
	for f in filter(lambda n: n.endswith('.bak'), os.listdir(FTP_DIR)):
		os.remove(os.path.join(FTP_DIR, f))
	for f in filter(lambda n: n.endswith('.txt'), os.listdir(FTP_DIR)):
			os.rename(os.path.join(FTP_DIR, f), os.path.join(FTP_DIR, f + '.bak'))

def downloadSymbols():
	files = ('nasdaqlisted.txt', 'otherlisted.txt')
	ftp = FTP('ftp.nasdaqtrader.com')
	ftp.login()
	ftp.cwd("SymbolDirectory")
	for f in files:
		mtime = ftp.sendcmd('MDTM ' + f).split()[1]
		name = f.split('.')[0] + '_' + mtime + '.txt'
		out = open(os.path.join(FTP_DIR, name), 'wb')
		ftp.retrbinary("RETR %s" % f, out.write)
		out.close()
	ftp.quit()

def reloadSymbols():
	'''Load symbols and metadata into sqlite'''

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

	# see http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs
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
			with open(os.path.join(FTP_DIR, f), 'rb') as csvfile:
				reader = csv.DictReader(csvfile, delimiter="|")
				for row in reader:
					tables = ('nasdaqlisted', 'otherlisted')
					if f.split('_')[0] in tables:
						cols = map(lambda s: s.replace(' ', '_').upper(), sorted(row.keys()))
						params = (f.split('_')[0], ','.join(cols))
						curs.execute("drop table if exists %s" % params[0])
						create = "create table %s (%s)" % params
						print create
						curs.execute(create)
						break
				for row in reader:
					qlst = []
					for unused in xrange(len(row.keys())):
						qlst.append('?')
					qms = ','.join(qlst)
					ins = 'insert into %s (%s) values (%s)' % (params[0], params[1], qms)
					curs.execute(ins, ([str(row[key]) for key in sorted(row.keys())]))
				conn.commit()
# 		for table in tables:
# 			last = 'select * from %s where rowid=%s' % (table , curs.execute('select max(rowid) from %s' % table).fetchone()[0])

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
	# magicCount = response.count(magicNum)
	if magicOffset > -1:
		try:
			# Ignore the 10-byte gzip file header and try to decompress the rest
			return zlib.decompress(response[magicOffset + 10:], -15)
		except zlib.error as e:
			raise e
	else:
		return response
