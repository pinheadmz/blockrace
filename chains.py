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
		print('Price:  ' + self.price)
		print('Hash:   ' + self.tipHash)
		print('Height: ' + self.tipHeight)
		print('# Txs:  ' + self.numTxs)

	def getPrice(self):
		self.price = Ticker.getPrice(self.sym)
		return self.price

	### different functions for each coin, delegated by __init__
	def BTC_getTip(self):
		r = requests.get("https://blockchain.info/latestblock").text
		j = json.loads(r)
		self.tipHeight = str(j["height"])
		self.tipHash = str(j["hash"])
		self.numTxs = str(len(j["txIndexes"]))

	def XMR_getTip(self):
		r = requests.get("https://xmrchain.net/api/transactions").text
		j = json.loads(r)
		self.tipHeight = str(j["data"]["blocks"][0]["height"])
		self.tipHash = str(j["data"]["blocks"][0]["hash"])
		self.numTxs = str(len(j["data"]["blocks"][0]["txs"]))

	def ETH_getTip(self):
		r = requests.get("https://etherchain.org/api/blocks/0/1").text
		j = json.loads(r)
		self.tipHeight = str(j["data"][0]["number"])
		self.tipHash = str(j["data"][0]["hash"])
		self.numTxs = str(j["data"][0]["tx_count"])

	def LTC_getTip(self):
		r = requests.get("https://chain.so/api/v2/get_info/ltc").text
		j = json.loads(r)
		self.tipHeight = str(j["data"]["blocks"])
		r = requests.get("https://chain.so/api/v2/get_block/ltc/" + self.tipHeight).text
		j = json.loads(r)
		self.tipHash = str(j["data"]["blockhash"])
		self.numTxs = str(len(j["data"]["txs"]))

	def DCR_getTip(self):
		r = requests.get("https://mainnet.decred.org/api/blocks?limit=0").text
		j = json.loads(r)
		self.tipHeight = str(j["blocks"][0]["height"])
		self.tipHash = str(j["blocks"][0]["hash"])
		self.numTxs = str(j["blocks"][0]["txlength"])
	
x = [Chain("Bitcoin", "BTC"),Chain("Monero", "XMR"),Chain("Ethereum", "ETH"),Chain("Litecoin", "LTC"),Chain("Decred", "DCR")]	

Ticker = Ticker()
Ticker.refresh()

for i in x:
	i.getTip()
	i.getPrice()
	i.display()
	print "--"