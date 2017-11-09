class Track():
	def __init__(self, id, G):
		self.id = id
		self.screens = G['screens']
		self.strips = G['strips']
		self.chain = False
		self.vis = 'flag'

	def setChain(self, chain):
		self.chain = chain

	def setVis(self, vis):
		self.vis = vis

	def refresh(self):
		if not self.chain:
			return False

		if self.screens:
			if self.vis == 'flag':
				self.screens.showLogoWithText(self.id, self.chain.logo, self.chain.name, (255, 255, 255))
			if self.vis == 'blocks':
				height = self.chain.history[-1].height
				text = self.chain.sym + ": " + height
				self.screens.showLogoWithText(self.id, self.chain.logo, text, (255, 255, 255))
			if self.vis == 'price':
				price = self.chain.price
				price = '${:,.2f}'.format(float(price))
				text = self.chain.sym + ": " + price
				self.screens.showLogoWithText(self.id, self.chain.logo, text, (255, 255, 255))
			if self.vis == 'txs':
				numTxs = self.chain.history[-1].numTxs
				text = self.chain.sym + ": " + numTxs
				self.screens.showLogoWithText(self.id, self.chain.logo, text, (255, 255, 255))

		if self.strips:
			if self.vis == 'flag':
				self.strips.twinkle(self.id, self.chain.color)
			if self.vis == 'blocks':
				self.strips.blocks(self.id, self.chain.color, self.chain.interval, self.chain.history)
			if self.vis == 'price':
				return
			if self.vis == 'txs':
				return
