from SocketServer import ThreadingTCPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from urlparse import urlparse, parse_qs
import sys
sys.path.append(r".\code")
from macd import getMacd	#@UnresolvedImport
from symbols import getSyms	#@UnresolvedImport
from obv import getObv	#@UnresolvedImport
from history import getHistory	#@UnresolvedImport

PORT = 80

urls = {'/macd.json': getMacd,
		'/symbols.json': getSyms,
		'/obv.json': getObv,
		'/history.json': getHistory}

class CustomHandler(SimpleHTTPRequestHandler):
	
	def end_headers(self):
		self.send_header('Access-Control-Allow-Origin', '*')
		SimpleHTTPRequestHandler.end_headers(self)
	
	def do_GET(self):
		url = urlparse(self.path)
		
		if url.path in urls:
			self.send_response(200)
			self.end_headers()
			self.wfile.write(urls[url.path](parse_qs(url.query)))
			return
		
		else:
			SimpleHTTPRequestHandler.do_GET(self)

httpd = ThreadingTCPServer(('localhost', PORT), CustomHandler)
sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()