from SocketServer import ThreadingTCPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from urlparse import urlparse, parse_qs
import multiprocessing as multi
import time
from const import pjoin
import const
import os
import sys
sys.path.append(r".\code")

from macd import getMacd  # @UnresolvedImport
from symbols import getSyms  # @UnresolvedImport
from obv import getObv  # @UnresolvedImport
from eod import getEod  # @UnresolvedImport
from history import getHistory  # @UnresolvedImport


if __name__ == '__main__':
	
	PORT = 80
	
	dynurls = {
			'/macd.json': getMacd,
			'/symbols.json': getSyms,
			'/obv.json': getObv,
			'/history.json': getHistory,
			'/eod.json' : getEod
			}
	
	# staturls = []
	
	cacheable = ['/history.json']
	cache = {}
	
	class CustomHandler(SimpleHTTPRequestHandler):
		
		def end_headers(self):
			''' No longer necessary, leaving as example '''
			# self.send_header('Access-Control-Allow-Origin', '*')
			SimpleHTTPRequestHandler.end_headers(self)
		
		def do_GET(self):
			url = urlparse(self.path)
			params = parse_qs(url.query)
			
			if url.path in dynurls:
				self.send_response(200)
				self.end_headers()
				
				if url.path in cacheable:
					if url.path in cache:
						self.wfile.write(cache[url.path])
					else:
						if url.path == '/history.json':
							params['pool'] = multi.Pool(3)
						cache[url.path] = dynurls[url.path](params)
						self.wfile.write(cache[url.path])
				else:
					self.wfile.write(dynurls[url.path](params))
			else:
				last = self.headers.get("If-Modified-Since")
				if last:
					cachetime = time.mktime(time.strptime(last, "%a, %d %b %Y %H:%M:%S GMT"))
# 					latest = time.mktime(time.gmtime(os.path.getmtime('.' + self.path)))
					latest = time.mktime(time.gmtime(os.path.getmtime('.' + self.path)))
					
					print self.path
					print cachetime
					print latest
					print (latest - cachetime) / 60
					
					if cachetime < latest:
						SimpleHTTPRequestHandler.do_GET(self)
					else:
						self.send_response(304)
						self.end_headers()
				else:
					SimpleHTTPRequestHandler.do_GET(self)
	
	
	httpd = ThreadingTCPServer(('localhost', PORT), CustomHandler)
	sa = httpd.socket.getsockname()
	print "Serving HTTP on", sa[0], "port", sa[1], "..."
	httpd.serve_forever()
