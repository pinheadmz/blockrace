import requests
import json


def jsonPP(string):
	print json.dumps(json.loads(string), indent=4, sort_keys=True)

class Ticker:
	def refresh(self):
		self.data = requests.get("https://api.coinmarketcap.com/v1/ticker").json()

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
		j = requests.get("https://blockchain.info/latestblock").json()
		self.tipHeight = str(j["height"])
		self.tipHash = str(j["hash"])
		self.numTxs = str(len(j["txIndexes"]))
		
	def BCH_getTip(self):
		j = requests.get("https://api.blockchair.com/bitcoin-cash/blocks").json()
		self.tipHeight = str(j["data"][0]["id"])
		self.tipHash = str(j["data"][0]["hash"])
		self.numTxs = str(j["data"][0]["transaction_count"])

	def ETH_getTip(self):
		j = requests.get("https://etherchain.org/api/blocks/0/1").json()
		self.tipHeight = str(j["data"][0]["number"])
		self.tipHash = str(j["data"][0]["hash"])
		self.numTxs = str(j["data"][0]["tx_count"])
		
	def ETC_getTip(self):
		j = requests.get("https://api.gastracker.io/blocks/latest").json()
		self.tipHeight = str(j["items"][0]["height"])
		self.tipHash = str(j["items"][0]["hash"])
		self.numTxs = str(j["items"][0]["transactions"])		

	def XMR_getTip(self):
		j = requests.get("https://xmrchain.net/api/transactions").json()
		self.tipHeight = str(j["data"]["blocks"][0]["height"])
		self.tipHash = str(j["data"]["blocks"][0]["hash"])
		self.numTxs = str(len(j["data"]["blocks"][0]["txs"]))

	def LTC_getTip(self):
		j = requests.get("https://chain.so/api/v2/get_info/ltc").json()
		self.tipHeight = str(j["data"]["blocks"])
		j = requests.get("https://chain.so/api/v2/get_block/ltc/" + self.tipHeight).json()
		self.tipHash = str(j["data"]["blockhash"])
		self.numTxs = str(len(j["data"]["txs"]))

	def DCR_getTip(self):
		j = requests.get("https://mainnet.decred.org/api/blocks?limit=0").json()
		self.tipHeight = str(j["blocks"][0]["height"])
		self.tipHash = str(j["blocks"][0]["hash"])
		self.numTxs = str(j["blocks"][0]["txlength"])
	
x = [Chain("Bitcoin", "BTC"),Chain("Bitcoin Cash", "BCH"),Chain("Ethereum", "ETH"),Chain("Ethereum Classic", "ETC"),Chain("Monero", "XMR"),Chain("Litecoin", "LTC"),Chain("Decred", "DCR")]	

Ticker = Ticker()
Ticker.refresh()

for i in x:
	i.getTip()
	i.getPrice()
	i.display()
	print "--"
