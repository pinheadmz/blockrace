from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from os import curdir, sep
import json
import operator
from multiprocessing.dummy import Pool as ThreadPool
import thread
import atexit

# configure hardware
SCREENS_ON = False
STRIPS_ON = False

# import other blockrace modules
if SCREENS_ON:
	from screens import *
if STRIPS_ON:
	from strips import *
from chains import *
from tracks import *

# CONSTANTS
API_TIMEOUT = 10
API_REFRESH = 3
VIS_REFRESH = 0.001
# 			index			name				sym		logo			color		interval	timeout
index = {	"BTC":	Chain("Bitcoin",			"BTC",	"bitcoin",		(255,153,0),	600,	API_TIMEOUT),
			"BCH":	Chain("Bitcoin Cash",		"BCH",	"bitcoin-cash",	(55,200,0),		600,	API_TIMEOUT),
			"ETH":	Chain("Ethereum",			"ETH",	"ethereum",		(0,153,200),	12,		API_TIMEOUT),
			"ETC":	Chain("Ethereum Classic",	"ETC",	"ethereum-classic", (0,253,100),12	,	API_TIMEOUT),
			"XMR":	Chain("Monero",				"XMR",	"monero",		(255,0,0),		120,	API_TIMEOUT),
			"LTC":	Chain("Litecoin",			"LTC",	"litecoin",		(0,0,255),		150,	API_TIMEOUT),
			"DCR":	Chain("Decred",				"DCR",	"decred",		(0,255,0),		300,	API_TIMEOUT)
		}
chains = [index["BTC"], index["BCH"], index["ETH"], index["ETC"], index["XMR"], index["LTC"], index["DCR"]]
ticker = Ticker(API_TIMEOUT)
G = {}
G['screens'] = Screens() if SCREENS_ON else False
G['strips'] = Strips() if STRIPS_ON else False
tracks = [Track(0, G), Track(1, G), Track(2, G), Track(3, G)]

# cleanup at shutdown
RUN_THREADS = True
def cleanup():
	# switch off flag to kill threads
	global RUN_THREADS, G
	RUN_THREADS = False
	# clear screens and lights
	print "Cleanup: stopping visualizers:"
	print G
	if G['screens']:
		G['screens'].clearAll()
		G['screens'] = False
	if G['strips']:
		G['strips'].allOff()
		G['strips'] = False
atexit.register(cleanup)

# TODO: check for internet and fail gracefully

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
	print "Starting http server..."
	httpd.serve_forever()
thread.start_new_thread(startServer, ())

# refresh screens and strips for each track in background thread
def animate():
	global G
	while RUN_THREADS:
		for t in tracks:
			t.refresh()
		if G['strips']:
			G['strips'].strip.show()
		time.sleep(VIS_REFRESH)
	# stop and clear when run flag is killed
	print "Animate: stopping visualizers:"
	print G
	if G['strips']:
		G['strips'].allOff()
		G['strips'] = False
	if G['screens']:
		G['screens'].clearAll()
		G['screens'] = False
thread.start_new_thread(animate, ())


# API refresh loop
pool = ThreadPool(8)
tick = 0
while True:
	# refresh price data
	ticker.refresh()
	# refresh chain data from APIs in multiple threads
	a = pool.map(operator.methodcaller('refresh'), chains)
	b = pool.map(operator.methodcaller('getPrice', ticker), chains)
	## print debug info to screen
	#os.system('clear')
	#for i in chains:
	#	i.display()
	#index['BTC'].display()
	time.sleep(API_REFRESH)
