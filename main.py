from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from os import curdir, sep
import json

class HTTPHandler(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_HEAD(self):
		self._set_headers()

	def do_GET(self):
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
		#data = json.loads(self.data_string)
		print(self.data_string)
		#self.wfile.write("Track: " + data["track"] + " = " + data["name"])
		return

def run(server_class=HTTPServer, handler_class=HTTPHandler, port=8080):
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	print 'Starting httpd...'
	httpd.serve_forever()

run()