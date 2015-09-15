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
	
	needspool = ['/history.json']
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
						if url.path in needspool:
							params['pool'] = multi.Pool(3)
						cache[url.path] = dynurls[url.path](params)
						self.wfile.write(cache[url.path])
				else:
					self.wfile.write(dynurls[url.path](params))
			
			elif self.headers.get("If-Modified-Since"):
				
				client_tmstruct = time.strptime(self.headers.get("If-Modified-Since"), "%a, %d %b %Y %H:%M:%S GMT")
				
				# Convert from immutable named-tuple to mutable list
				writable = list(time.gmtime(os.path.getmtime('.' + url.path)))
				
				# Set 'tm_isdst' value for local file equal to value from client header
				writable[-1] = client_tmstruct[-1]
				last_modtime = time.mktime(time.struct_time(tuple(writable)))

				if last_modtime > time.mktime(client_tmstruct):
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
