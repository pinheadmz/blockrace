# configure hardware
SCREENS_ON = False
STRIPS_ON = False

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from os import curdir, sep
import json
import operator
from multiprocessing.dummy import Pool as ThreadPool
import thread
import atexit

# import other blockrace modules
from chains import *
from tracks import *
if SCREENS_ON:
	from screens import *
if STRIPS_ON:
	from strips import *

# CONSTANTS
# 			index			name				sym		logo			color		interval
index = {	"BTC":	Chain("Bitcoin",			"BTC",	"bitcoin",		(255,153,0),	600),
			"BCH":	Chain("Bitcoin Cash",		"BCH",	"bitcoin-cash",	(55,200,0),		600),
			"ETH":	Chain("Ethereum",			"ETH",	"ethereum",		(0,153,200),	12),
			"ETC":	Chain("Ethereum Classic",	"ETC",	"ethereum-classic", (0,253,100),12),
			"XMR":	Chain("Monero",				"XMR",	"monero",		(255,0,0),		120),
			"LTC":	Chain("Litecoin",			"LTC",	"litecoin",		(0,0,255),		150),
			"DCR":	Chain("Decred",				"DCR",	"decred",		(0,255,0),		300)
		}
chains = [index["BTC"], index["BCH"], index["ETH"], index["ETC"], index["XMR"], index["LTC"], index["DCR"]]
tracks = [Track(0), Track(1), Track(2), Track(3)]
if SCREENS_ON:
	screens = Screens()
if STRIPS_ON:
	strips = Strips()
API_REFRESH = 3
VIS_REFRESH = 0.25

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
		# DYNAMICALLY GENERATED js file - special GET case
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

		# main UI page
		if self.path == "/":
			self.path = "index.html"

		# GET the requested file from /www
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

		# user requesting info for a chain to display on the touchscreen
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

		# user selecting a chain for a track
		if self.path == "/trackSelectedChain":
			track = data['track']
			chosenChain = index[data['sym']]
			tracks[track].setChain(chosenChain)
			self.wfile.write(json.dumps({"success": True}))

		# user choosing a display mode for LED strips and screens text
		if self.path == "/setVis":
			track = data['track']
			visChoice = data['visChoice']
			tracks[track].setVis(visChoice)
			self.wfile.write(json.dumps({"success": True}))
		return

# start the web server in a background thread
def startServer(server_class=HTTPServer, handler_class=HTTPHandler, port=8080):
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	print 'Starting httpd...'
	httpd.serve_forever()
thread.start_new_thread(startServer, ())

## MAIN LOOP ##
pool = ThreadPool(8)
while True:
	# refresh price data
	Ticker.refresh()
	# refresh chain data from APIs in multiple threads
	a = pool.map(operator.methodcaller('refresh'), chains)
	b = pool.map(operator.methodcaller('getPrice'), chains)
	## print debug info to screen
	#os.system('clear')
	#for i in chains:
	#	i.display()
	# refresh screens and strips for each track - ALSO API REFRESH
	tick = 0
	while tick < API_REFRESH:
		for t in tracks:
			t.refresh()
		time.sleep(VIS_REFRESH)
		tick += VIS_REFRESH
