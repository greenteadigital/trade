from datetime import date, timedelta
import dllib
import os
import csv
import urllib2
from cStringIO import StringIO as strio
import const
from const import pjoin
from fnmatch import fnmatch
import sys

# build URLs with symbols and intended date range
# make requests to yahoo in round-robin fashion
def downloadEodData():
	txts = filter(lambda fn: fnmatch(fn, '*listed_*.txt'), os.listdir(const.SYM_DIR))
	
	nsdl = filter(lambda fn: fnmatch(fn, 'nasdaqlisted_*.txt'), txts)[0]
# 	print nsdl
	allnsd = list(csv.DictReader(open(pjoin(const.SYM_DIR, nsdl), 'rb'), delimiter="|"))
	nsdsyms = filter(lambda s: s.isalpha(), map(lambda d: d['Symbol'], allnsd))
	
	othl = filter(lambda fn: fnmatch(fn, 'otherlisted_*.txt'), txts)[0]
	allother = list(csv.DictReader(open(pjoin(const.SYM_DIR, othl), 'rb'), delimiter="|"))
	othsyms = filter(lambda s: s.isalpha(), map(lambda d: d['ACT Symbol'], allother))
	
	txt_syms = nsdsyms + othsyms
	txt_syms.sort()
	for s in txt_syms:
		print s
	sys.exit()
	
# 	txt_syms = 
	fs_syms = map(lambda n: n.split('.')[0], os.listdir(const.RAW_DIR))
	syms = filter(lambda i: i.isalpha(), map(lambda i: i.lstrip('_'), list(set(txt_syms) - set(fs_syms))))
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
downloadEodData()


# EOF
