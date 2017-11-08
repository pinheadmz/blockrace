from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from os import curdir, sep
import json
import operator
from multiprocessing.dummy import Pool as ThreadPool
import thread
import atexit

from chains import *

SCREENS_ON = True
STRIPS_ON = True
if SCREENS_ON:
	from screens import *
if STRIPS_ON:
	from strips import *

# CONSTANTS
index = {	"BTC":	Chain("Bitcoin",			"BTC",	"bitcoin",		(255,153,0)),
			"BCH":	Chain("Bitcoin Cash",		"BCH",	"bitcoin-cash",	(55,200,0)),
			"ETH":	Chain("Ethereum",			"ETH",	"ethereum",		(0,153,200)),
			"ETC":	Chain("Ethereum Classic",	"ETC",	"ethereum-classic", (0,253,100)),
			"XMR":	Chain("Monero",				"XMR",	"monero",		(255,0,0)),
			"LTC":	Chain("Litecoin",			"LTC",	"litecoin",		(0,0,255)),
			"DCR":	Chain("Decred",				"DCR",	"decred",		(0,255,0))
		}
chains = [index["BTC"], index["BCH"], index["ETH"], index["ETC"], index["XMR"], index["LTC"], index["DCR"]]
if SCREENS_ON:
	screens = Screens()
if STRIPS_ON:
	strips = Strips()


# cleanup at shutdown
def cleanup():
	# clear screens and lights
	if SCREENS_ON:
		screens.clearAll()
	if STRIPS_ON:
		strips.allOff()
atexit.register(cleanup)

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

		if self.path == "/trackSelectedChain":
			chosenChain = index[data['sym']]
			track = data['track']
			# push logo to screen
			if SCREENS_ON:
				screens.showLogo(track, chosenChain.logo)
			# TEST turn on some LEDS!
			if STRIPS_ON:
				strips.stripe(int(track-1)*75, int(track-1)*75+75, *chosenChain.color)
			self.wfile.write(json.dumps({"success": True}))

		if self.path == "/getChainInfo":
			chosenChain = index[data['sym']]
			# respond to browser
			self.wfile.write(json.dumps({	"name": chosenChain.name,
											"price": chosenChain.price,
											"hourPriceChange": chosenChain.hourPriceChange,
											"dayPriceChange": chosenChain.dayPriceChange,
											"height": chosenChain.history[-1].height,
											"numTxs": chosenChain.history[-1].numTxs,
											"time": chosenChain.history[-1].time,
											"hash": chosenChain.history[-1].hash,
											"netstat": chosenChain.netstat
										}))

		if self.path == "/setVis":
			# TODO
			print(json.dumps(data))
			self.wfile.write(json.dumps(data))
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
