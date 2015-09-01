from datetime import date, timedelta
import dllib
import os
import csv
import urllib2
import const
from const import pjoin, pexists
from fnmatch import fnmatch
import re
# import sys


def getStartDate(sym):
	loc = pjoin(const.RAW_DIR, '_' + sym)
	if not pexists(loc):
		return (0, 1, 1900, '0')
	else:
		files = os.listdir(loc)
		files.sort()
		seq = re.split(r"[_\.]", files[-1])[2]
		nseq = str(int(seq) + 1)
		ldate = list(csv.DictReader(open(pjoin(loc, files[-1]), 'rb')))[0]['Date']
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
	syms.sort()
	for symbol in syms:
		ip2host = dllib.getIpMap()
		mo, dy, yr, seq = getStartDate(symbol)
		success = False
		for ip in ip2host:
			params = (ip, symbol, mo, dy, yr)
			url = "http://%s/table.csv?s=%s&a=%s&b=%s&c=%s&d=11&e=31&f=2099&g=d" % params
			
			print url
			break
			
			# TODO: set up round-robin to spread load across available hosts
			
			loc = urllib2.Request(url)
			loc.add_header('Accept-Encoding', 'gzip, deflate')
			loc.add_header('Host', ip2host[ip])
			opener = urllib2.build_opener()
			print 'requesting', url
			try:
				csv_txt = dllib.tryDecompress(opener.open(loc).read())
				_name = '_' + symbol
				outdir = pjoin(const.RAW_DIR, _name)
				if not pexists(outdir):
					os.mkdir(outdir)
				open(pjoin(outdir, _name + '_' + seq + '.csv'), 'wb').write(csv_txt)
				success = True
				break
			except urllib2.HTTPError:
				continue
		if success:
			print 'success', symbol
		else:
# 			print 'FAIL', symbol
			pass
		

# dllib.backupSymbols()
# dllib.downloadSymbols()
updateEodData()


# EOF
