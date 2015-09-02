import socket
from ftplib import FTP
import sqlite3
import os
import csv
import zlib
from const import SYM_DIR, DB_DIR, pjoin


def backupSymbols():
	''' Backup current symbol files and download latest symbols from nasdaq ftp '''
	files = os.listdir(SYM_DIR)
	for f in filter(lambda n: n.endswith('.bak'), files):
		os.remove(pjoin(SYM_DIR, f))
	for f in filter(lambda n: n.endswith('.txt'), files):
		os.rename(pjoin(SYM_DIR, f), pjoin(SYM_DIR, f + '.bak'))

def downloadSymbols():
	files = ('nasdaqlisted.txt', 'otherlisted.txt')
	ftp = FTP('ftp.nasdaqtrader.com')
	ftp.login()
	ftp.cwd("SymbolDirectory")
	for f in files:
		mtime = ftp.sendcmd('MDTM ' + f).split()[1]
		name = f.split('.')[0] + '_' + mtime + '.txt'
		out = open(pjoin(SYM_DIR, name), 'wb')
		ftp.retrbinary("RETR %s" % f, out.write)
		out.close()
	ftp.quit()

def reloadSymbols():
	'''Load symbols and metadata into sqlite'''
	# see http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs
	with sqlite3.connect(pjoin(DB_DIR, "symbols.db")) as conn:
		curs = conn.cursor()
		tables = ('nasdaqlisted', 'otherlisted')
		for f in filter(lambda n: n.endswith('.txt'), os.listdir(SYM_DIR)):
			with open(pjoin(SYM_DIR, f), 'rb') as csvfile:
				reader = csv.DictReader(csvfile, delimiter="|")
				for row in reader:
					if f.split('_')[0] in tables:
						cols = map(lambda s: s.replace(' ', '_').upper(), sorted(row.keys()))
						params = (f.split('_')[0], ','.join(cols))
						curs.execute("drop table if exists %s" % params[0])
						create = "create table %s (%s)" % params
						print create
						curs.execute(create)
						break
				for row in reader:
					qms = ','.join(list('?' * len(row.keys())))
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
	if magicOffset > -1:
		try:
			# Ignore the 10-byte gzip file header and try to decompress the rest
			return zlib.decompress(response[magicOffset + 10:], -15)
		except zlib.error as e:
			raise e
	else:
		return response
