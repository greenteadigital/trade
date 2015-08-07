from SocketServer import ThreadingTCPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from urlparse import urlparse, parse_qs
import sys
sys.path.append(r".\code")
from macd import getMacd	#@UnresolvedImport
from symbols import getSyms #@UnresolvedImport
from obv import getObv #@UnresolvedImport

PORT = 8080

class CustomHandler(SimpleHTTPRequestHandler):
	
	def end_headers(self):
		self.send_header('Access-Control-Allow-Origin', '*')
		SimpleHTTPRequestHandler.end_headers(self)
	
	def do_GET(self):
		url = urlparse(self.path)
		
		if url.path=='/macd.json':
			self.send_response(200)
			self.end_headers()
			self.wfile.write(getMacd(parse_qs(url.query)))
			return
		
		elif url.path=='/symbols.json':
			self.send_response(200)
			self.end_headers()
			self.wfile.write(getSyms())
			return
		
		elif url.path=='/obv.json':
			self.send_response(200)
			self.end_headers()
			self.wfile.write(getObv(parse_qs(url.query)))
			return
		
		else:
			SimpleHTTPRequestHandler.do_GET(self)

httpd = ThreadingTCPServer(('localhost', PORT), CustomHandler)
sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()