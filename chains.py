import requests
import json

def jsonPP(string):
	print json.dumps(json.loads(string), indent=4, sort_keys=True)

class Ticker:
	def refresh(self):
		r = requests.get("https://api.coinmarketcap.com/v1/ticker").text
		self.data = json.loads(r)
	
	def getPrice(self, sym):
		price = 0
		for c in self.data:
			if c["symbol"] == sym:
				price = c["price_usd"]
				break
		return price

class Chain:
	def __init__(self, name, sym):
		self.name=name
		self.sym=sym
		self.getTip=getattr(self, sym + "_getTip")
	
	def display(self):
		print('Name:   ' + self.name)
		print('Symbol: ' + self.sym)
		print('Height: ' + self.tipHeight)
		print('Hash:   ' + self.tipHash)
		print('Price:  ' + self.price)
	
	def getPrice(self):
		self.price = Ticker.getPrice(self.sym)
		return self.price
	
	def BTC_getTip(self):
		r = requests.get("https://blockchain.info/latestblock").text
		j = json.loads(r)
		self.tipHeight = str(j["height"])
		self.tipHash = str(j["hash"])
	
	

Ticker = Ticker()
Ticker.refresh()


x = [Chain("Bitcoin", "BTC")]

for i in x:
	i.getTip()
	i.getPrice()
	i.display()