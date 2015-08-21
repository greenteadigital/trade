import dllib
import os
import urllib2

def downloadSplitData():
	ip2host = dllib.getIpMap()
	syms = map(lambda n: n.lstrip('_').split('.')[0], os.listdir(dllib.EOD_DIR))
	for sym in syms:
		print sym
		ip2host = dllib.getIpMap()
		success = False
		for ip in ip2host:
			params = (ip, sym)
			url = "http://%s/x?s=%s&a=0&b=1&c=1900&d=11&e=31&f=2099&g=v&y=0&z=99999" % params
			loc = urllib2.Request(url)
			loc.add_header('Accept-Encoding', 'gzip, deflate')
			loc.add_header('Host', ip2host[ip])
			opener = urllib2.build_opener()
			print 'requesting', url
			try:
				csv_txt = dllib.tryDecompress(opener.open(loc).read())
				open(os.path.join(dllib.SPLIT_DIR, 'divsplit_' + sym + '.csv'), 'wb').write(csv_txt)
				success = True
				break
			except urllib2.HTTPError as err:
				continue
		if success:
			print 'success', sym
		else:
			print 'FAIL', sym

downloadSplitData()