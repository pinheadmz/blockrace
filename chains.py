import requests
import json
import time
import sys
import os
import operator
from multiprocessing.dummy import Pool as ThreadPool 

# Constants
IMG128_DIR = "/www/i/128/"
MAX_BLOCK_HISTORY = 60

# Utility
def jsonPP(string):
	print json.dumps(json.loads(string), indent=4, sort_keys=True)

# Object to refresh prices for all chains
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

# Object to store details about blocks
class Tip:
	def __init__(self, height, hash, numTxs):
		self.height = height
		self.hash = hash
		self.numTxs = numTxs
		self.time = int(time.time())

# Object for each chain
class Chain:
	def __init__(self, name, sym, logo):
		# general details for chain
		self.name = name
		self.sym = sym
		self.logo = IMG128_DIR + logo
		self.price = 0
		# store history of chain tips
		self.history = [Tip(0,0,0)]
		# delegate API function
		self.getTip = getattr(self, sym + "_getTip")
	
	def refresh(self):
		newTip = self.getTip()
		if not newTip:
			return False
		oldTip = self.history[-1]
		if newTip.height != oldTip.height:
			# clear init tip
			if oldTip.height == 0:
				self.history.pop(-1)
			self.history.append(newTip)
			if len(self.history) > MAX_BLOCK_HISTORY:
				self.history.pop(0)
			return newTip
		else:
			return False

	def display(self):
		print('---')
		print('Name:   ' + self.name)
		print('Symbol: ' + self.sym)
		print('Price:  ' + str(self.price))
		print('History:')
		for tip in self.history:
			print '%18.16s%14.12s%80.78s%10.8s' % (str(tip.time), str(tip.height), str(tip.hash), str(tip.numTxs))

	def getPrice(self):
		self.price = Ticker.getPrice(self.sym)
		return self.price

	### different functions for each coin, delegated by __init__
	def BTC_getTip(self):
		try:
			j = requests.get("https://blockchain.info/latestblock").json()
			tipHeight = str(j["height"])
			tipHash = str(j["hash"])
			tipNumTxs = str(len(j["txIndexes"]))
			return Tip(tipHeight, tipHash, tipNumTxs)
		except:
			print(self.name, "Error:", sys.exc_info())
			return False
		
	def BCH_getTip(self):
		try:
			j = requests.get("https://api.blockchair.com/bitcoin-cash/blocks").json()
			tipHeight = str(j["data"][0]["id"])
			tipHash = str(j["data"][0]["hash"])
			tipNumTxs = str(j["data"][0]["transaction_count"])
			return Tip(tipHeight, tipHash, tipNumTxs)
		except:
			print(self.name, "Error:", sys.exc_info())
			return False

	def ETH_getTip(self):
		try:
			j = requests.get("https://etherchain.org/api/blocks/0/1").json()
			tipHeight = str(j["data"][0]["number"])
			tipHash = str(j["data"][0]["hash"])
			tipNumTxs = str(j["data"][0]["tx_count"])
			return Tip(tipHeight, tipHash, tipNumTxs)
		except:
			print(self.name, "Error:", sys.exc_info())
			return False
		
	def ETC_getTip(self):
		try:
			j = requests.get("https://api.gastracker.io/blocks/latest").json()
			tipHeight = str(j["items"][0]["height"])
			tipHash = str(j["items"][0]["hash"])
			tipNumTxs = str(j["items"][0]["transactions"])	
			return Tip(tipHeight, tipHash, tipNumTxs)
		except:
			print(self.name, "Error:", sys.exc_info())
			return False

	def XMR_getTip(self):
		try:
			j = requests.get("https://xmrchain.net/api/transactions").json()
			tipHeight = str(j["data"]["blocks"][0]["height"])
			tipHash = str(j["data"]["blocks"][0]["hash"])
			tipNumTxs = str(len(j["data"]["blocks"][0]["txs"]))
			return Tip(tipHeight, tipHash, tipNumTxs)
		except:
			print(self.name, "Error:", sys.exc_info())
			return False

	def LTC_getTip(self):
		try:
			j = requests.get("https://chain.so/api/v2/get_info/ltc").json()
			tipHeight = str(j["data"]["blocks"])
			j = requests.get("https://chain.so/api/v2/get_block/ltc/" + tipHeight).json()
			tipHash = str(j["data"]["blockhash"])
			tipNumTxs = str(len(j["data"]["txs"]))
			return Tip(tipHeight, tipHash, tipNumTxs)
		except:
			print(self.name, "Error:", sys.exc_info())
			return False

	def DCR_getTip(self):
		try:
			j = requests.get("https://mainnet.decred.org/api/blocks?limit=0").json()
			tipHeight = str(j["blocks"][0]["height"])
			tipHash = str(j["blocks"][0]["hash"])
			tipNumTxs = str(j["blocks"][0]["txlength"])
			return Tip(tipHeight, tipHash, tipNumTxs)
		except:
			print(self.name, "Error:", sys.exc_info())
			return False
	
x = [	Chain("Bitcoin",			"BTC",	"bitcoin.png"),
		Chain("Bitcoin Cash",		"BCH",	"bitcoin-cash.png"),
		Chain("Ethereum",			"ETH",	"ethereum.png"),
		Chain("Ethereum Classic",	"ETC",	"ethereum-classic.png"),
		Chain("Monero",				"XMR",	"monero.png"),
		Chain("Litecoin",			"LTC",	"litecoin.png"),
		Chain("Decred",				"DCR",	"decred.png")
	]	

Ticker = Ticker()
Ticker.refresh()

pool = ThreadPool(8)

while True:
	a = pool.map(operator.methodcaller('refresh'), x)
	b = pool.map(operator.methodcaller('getPrice'), x)
	os.system('clear')
	for i in x:
		i.display()
	time.sleep(3)