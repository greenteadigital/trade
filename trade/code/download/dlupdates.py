from datetime import date, timedelta
import dllib
import os
import csv
import urllib2
import const
from const import pjoin, pexists
from fnmatch import fnmatch
import re
from lib.libadjust import mergeAndAdjust
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
		with open(pjoin(loc, files[-1]), 'rb') as histdata:
			ldate = list(csv.DictReader(histdata))[0]['Date']
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
			rrobin[targetip] += 1
			_name = '_' + symbol
			outdir = pjoin(const.RAW_DIR, _name)
			if not pexists(outdir):
				os.mkdir(outdir)
			open(pjoin(outdir, _name + '_' + seq + '.csv'), 'wb').write(csv_txt)
			print 'success', symbol
			mergeAndAdjust(symbol)
		except urllib2.HTTPError:
			print 'FAIL', symbol
		

dllib.backupSymbols()
dllib.downloadSymbols()
updateEodData()


# EOF
