from datetime import date, timedelta, datetime
import time
import dllib
import os
import csv
import urllib2
import cookielib
import ssl
import const
from const import pjoin, pexists, strio
from fnmatch import fnmatch
import re
from lib.libadjust import mergeAndAdjust
from zipfile import ZipFile, ZIP_DEFLATED
import sys
import base64 
BAD_SYMS = ['OHGI']

AGENT = ('Mozilla/5.0 (Windows NT 6.0; Win64; x64) AppleWebKit/523.1 ' +
		'(KHTML, like Gecko) Chrome/56.0.2421.100 Safari/525.1')
CJ = cookielib.CookieJar()

def getStartDate(sym):
	loc = pjoin(const.RAW_DIR, '_' + sym + '.csv.zip')
	if not pexists(loc):
		dt = datetime(1950, 1, 1, 0, 0)
		start = str(int(time.mktime(dt.timetuple())))
		return (start, '0')
	else:
		with ZipFile(loc, 'r', ZIP_DEFLATED) as _zip:
			files = filter(lambda n: n.find("MACOSX") == -1 and n.find("DS_Store") == -1, _zip.namelist())
			
# 			for f in filter(lambda n: n.find("MACOSX") == -1 and n.find("DS_Store") == -1, files):
# 				print f
# 			return
			
			files.sort()
			seq = re.split(r"[_\.]", files[-1].split('/')[-1])[2]
			nseq = str(int(seq) + 1)
			ldate = list(csv.DictReader(strio(_zip.read(files[-1]))))[0]['Date']
# 			print ldate
			yr, mo, dy = map(int, ldate.split('-'))
			dt = (datetime(yr, mo, dy, 0, 0) + timedelta(days=1))
			nxt = str(int(time.mktime(dt.timetuple())))
			return (nxt, nseq)

def getSymbols():
	txts = filter(lambda fn: fnmatch(fn, '*listed_*.txt'), os.listdir(const.SYM_DIR))
	
	nsdl = filter(lambda fn: fnmatch(fn, 'nasdaqlisted_*.txt'), txts)[0]
	allnsd = list(csv.DictReader(open(pjoin(const.SYM_DIR, nsdl), 'rb'), delimiter="|"))
	nsdsyms = filter(lambda s: s.isalpha(), map(lambda d: d['Symbol'], allnsd))
	
	othl = filter(lambda fn: fnmatch(fn, 'otherlisted_*.txt'), txts)[0]
	allother = list(csv.DictReader(open(pjoin(const.SYM_DIR, othl), 'rb'), delimiter="|"))
	othsyms = filter(lambda s: s.isalpha(), map(lambda d: d['ACT Symbol'], allother))
	
	txt_syms = nsdsyms + othsyms
	
	raw_syms = map(lambda n: n.split('.')[0][1:], os.listdir(const.RAW_DIR))
	syms = list(set(txt_syms + raw_syms))
	for sym in BAD_SYMS:
		syms.remove(sym)
	syms.sort()
	return syms

def updateEodData():
	
	syms = getSymbols()
	
	# # TEMPORARY TRUNCATION, REMOVE
# 	LAST = 'TROVW'
# 	syms = syms[syms.index(LAST) + 1 :]

# 	rrobin = {}
	crumb = getCrumb()
	
	for symbol in syms:
		p1, seq = getStartDate(symbol)
		p2 = str(int(time.mktime(datetime.today().timetuple())))
# 		ip2host = dllib.getIpMap()

		# Get target ip in round-robin fashion
# 		for ip in ip2host:
# 			if ip not in rrobin:
# 				rrobin[ip] = 0
# 				targetip = ip
# 			else:
# 				ld = [{count : ip} for ip, count in rrobin.items()]
# 				ld = filter(lambda d: d.values()[0] in ip2host, ld)
# 				ld.sort()
# 				targetip = ld[0].values()[0]

		params = (base64.b64decode('cXVlcnkxLmZpbmFuY2UueWFob28uY29t'), symbol, p1, p2, crumb)
		quoteUrl = "https://%s/v7/finance/download/%s?period1=%s&period2=%s&interval=1d&events=history&crumb=%s" % params
		loc = urllib2.Request(quoteUrl)
		loc.add_header('Accept-Encoding', 'gzip, deflate')
		loc.add_header('User-Agent', AGENT)
# 		loc.add_header('Host', ip2host[targetip])
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CJ))
		print 'requesting', quoteUrl
		try:
			csv_txt = dllib.tryDecompress(opener.open(loc).read())
			if list(csv.DictReader(strio(csv_txt))):
# 				rrobin[targetip] += 1
				_name = '_' + symbol
				zname = _name + '.csv.zip'
				with ZipFile(pjoin(const.RAW_DIR, zname), 'a', ZIP_DEFLATED) as _zip:
					_zip.writestr(_name + '_' + seq + '.csv', csv_txt)
				print 'success', symbol
				mergeAndAdjust(symbol)
		except urllib2.HTTPError as e:
			print e
			print 'FAIL', symbol
# 		except ssl.CertificateError:
# 			pass

def getCrumb():
	cookieUrl = base64.b64decode('aHR0cHM6Ly9maW5hbmNlLnlhaG9vLmNvbQ==')
	crumbUrl = base64.b64decode('aHR0cHM6Ly9xdWVyeTEuZmluYW5jZS55YWhvby5jb20vdjEvdGVzdC9nZXRjcnVtYg==')
	loc = urllib2.Request(cookieUrl)
	loc.add_header('User-Agent', AGENT)

	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CJ))
	opener.open(loc)
	return opener.open(crumbUrl).read()
	
if __name__ == '__main__':
# 	dllib.backupSymbols()
# 	dllib.downloadSymbols()
# 	updateEodData()
# 	syms = getSymbols()
	
	# # TEMPORARY TRUNCATION, REMOVE
# 	LAST = 'KLD'
# 	syms = syms[syms.index(LAST):]
	
	print getStartDate('GTY')
	sys.exit()
	
	for sym in getSymbols():
		if sym:
			print '[' + sym + ']'
			try:
				mergeAndAdjust(sym)
			except IOError as e:
				if e.errno == 2:
					pass
				else:
					raise e


# EOF
