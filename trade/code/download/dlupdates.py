from datetime import date, timedelta
import dllib
import os
import csv
import urllib2
import const
from const import pjoin, pexists, strio
from fnmatch import fnmatch
import re
from lib.libadjust import mergeAndAdjust
from zipfile import ZipFile, ZIP_DEFLATED

BAD_SYMS = ['OHGI']

def getStartDate(sym):
	loc = pjoin(const.RAW_DIR, '_' + sym + '.csv.zip')
	if not pexists(loc):
		return (0, 1, 1900, '0')
	else:
		with ZipFile(loc, 'r', ZIP_DEFLATED) as _zip:
			files = _zip.namelist()
			files.sort()
			seq = re.split(r"[_\.]", files[-1])[2]
			nseq = str(int(seq) + 1)
			ldate = list(csv.DictReader(strio(_zip.read(files[-1]))))[0]['Date']
			yr, mo, dy = map(int, ldate.split('-'))
			nxt = date(yr, mo, dy) + timedelta(days=1)
			return (nxt.month - 1, nxt.day, nxt.year, nseq)


def updateEodData():
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
	
	# # TEMPORARY TRUNCATION, REMOVE
# 	LAST = 'OHAI'
# 	syms = syms[syms.index(LAST) + 1 :]

	rrobin = {}
	for symbol in syms:
		mo, dy, yr, seq = getStartDate(symbol)
		ip2host = dllib.getIpMap()

		# Get target ip in round-robin fashion
		for ip in ip2host:
			if ip not in rrobin:
				rrobin[ip] = 0
				targetip = ip
			else:
				ld = [{count : ip} for ip, count in rrobin.items()]
				ld = filter(lambda d: d.values()[0] in ip2host, ld)
				ld.sort()
				targetip = ld[0].values()[0]

		params = (targetip, symbol, mo, dy, yr)
		url = "http://%s/table.csv?s=%s&a=%s&b=%s&c=%s&d=11&e=31&f=2099&g=d" % params
		loc = urllib2.Request(url)
		loc.add_header('Accept-Encoding', 'gzip, deflate')
		loc.add_header('Host', ip2host[targetip])
		opener = urllib2.build_opener()
		print 'requesting', url
		try:
			csv_txt = dllib.tryDecompress(opener.open(loc).read())
			if list(csv.DictReader(strio(csv_txt))):
				rrobin[targetip] += 1
				_name = '_' + symbol
				zname = _name + '.csv.zip'
				with ZipFile(pjoin(const.RAW_DIR, zname), 'a', ZIP_DEFLATED) as _zip:
					_zip.writestr(_name + '_' + seq + '.csv', csv_txt)
				print 'success', symbol
				mergeAndAdjust(symbol)
		except urllib2.HTTPError:
			print 'FAIL', symbol
		
if __name__ == '__main__':
	dllib.backupSymbols()
	dllib.downloadSymbols()
	updateEodData()


# EOF
