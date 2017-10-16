from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from os import curdir, sep
import json
import operator
from multiprocessing.dummy import Pool as ThreadPool 
import thread
from chains import *

# CONSTANTS
index = {	"BTC":	Chain("Bitcoin",			"BTC",	"bitcoin.png"),
			"BCH":	Chain("Bitcoin Cash",		"BCH",	"bitcoin-cash.png"),
			"ETH":	Chain("Ethereum",			"ETH",	"ethereum.png"),
			"ETC":	Chain("Ethereum Classic",	"ETC",	"ethereum-classic.png"),
			"XMR":	Chain("Monero",				"XMR",	"monero.png"),
			"LTC":	Chain("Litecoin",			"LTC",	"litecoin.png"),
			"DCR":	Chain("Decred",				"DCR",	"decred.png")
		}	
chains = [index["BTC"], index["BCH"], index["ETH"], index["ETC"], index["XMR"], index["LTC"], index["DCR"]]

# WEB SERVER
class HTTPHandler(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_HEAD(self):
		self._set_headers()

	def do_GET(self):
		# DYNAMIC js file
		if self.path == "/chainsIndex.js":
			chainsIndex = []
			for chain in chains:
				chainObj = {}
				chainObj["name"] = chain.name
				chainObj["sym"] = chain.sym
				chainObj["logo"] = chain.logo
				chainsIndex.append(chainObj)
			jsString = "chains="+json.dumps(chainsIndex)
			self.send_response(200)
			self.send_header('Content-type','application/javascript')
			self.end_headers()
			self.wfile.write(jsString)
			return
	
		if self.path == "/":
			self.path = "index.html"
		try:
			#Check the file extension required and set the right mime type
			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			if self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			if self.path.endswith(".png"):
				mimetype='image/png'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True

			if sendReply == True:
				#Open the static file requested and send it
				f = open(curdir + sep + "www" + sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			else:
				self.send_error(404,'File Type Unknown: %s' % self.path)
		except:
			self.send_error(404,'File Not Found: %s' % self.path)
		return

	def do_POST(self):
		self._set_headers()
		self.data_string = self.rfile.read(int(self.headers['Content-Length']))
		data = json.loads(self.data_string)
		chosenChain = index[data['sym']]
		self.wfile.write(json.dumps({	"name": chosenChain.name,
										"price": chosenChain.price,
										"height": chosenChain.getTip().height,
										"hash": chosenChain.getTip().hash
									}))
		return

def startServer(server_class=HTTPServer, handler_class=HTTPHandler, port=8080):
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	print 'Starting httpd...'
	httpd.serve_forever()

# start the web server in a background thread
thread.start_new_thread(startServer, ())

# START API SCRAPER
pool = ThreadPool(8)
while True:
	Ticker.refresh()
	a = pool.map(operator.methodcaller('refresh'), chains)
	b = pool.map(operator.methodcaller('getPrice'), chains)
	os.system('clear')
	for i in chains:
		i.display()
	time.sleep(3)