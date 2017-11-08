class Track():
	def __init__(self, id):
		self.id = id
		self.chain = False
		self.vis = 'flag'
	
	def setChain(self, chain):
		self.chain = chain

	def setVis(self, vis):
		self.vis = vis

	def refresh(self):
		if not self.chain:
			return False

		if SCREENS_ON:
			if self.vis == 'flag':
				screens.showLogoWithText(self.id, self.chain.logo, self.chain.name, (255, 255, 255)):
			if self.vis == 'blocks':
				height = self.chain.history[-1].height
				text = self.chain.sym + ": " + height
				screens.showLogoWithText(self.id, self.chain.logo, text, (255, 255, 255)):
			if self.vis == 'price':
				price = self.chain.price
				price = '${:,.2f}'.format(float(price))
				text = self.chain.sym + ": " + price
				screens.showLogoWithText(self.id, self.chain.logo, text, (255, 255, 255)):
			if self.vis == 'txs':
				numTxs = self.chain.history[-1].numTxs
				text = self.chain.sym + ": " + numTxs
				screens.showLogoWithText(self.id, self.chain.logo, text, (255, 255, 255)):

		if STRIPS_ON:
			if self.vis == 'flag':
				strips.twinkle(self.id, self.chain.color)
			if self.vis == 'blocks':
				
				strips.twinkle(self.id, self.chain.color, pattern)
			if self.vis == 'price':

			if self.vis == 'txs':
