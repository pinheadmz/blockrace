from PIL import Image, ImageDraw, ImageFont
import PIL.ImageOps
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import time

# constants for ST7735 and image objects
WIDTH = 128
HEIGHT = 160
SPEED_HZ = 4000000
IMG_DIR = '/home/pi/blockrace/jpg128/'
LOGO_HEIGHT = 128

# Raspberry Pi configuration
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

class Screens():
	def __init__(self):
		self.csPins = [14, 15, 23, 7]
		self.gpio = GPIO.get_platform_gpio()
		for p in self.csPins:
			self.gpio.setup(p, GPIO.OUT)
		self.disp = TFT.ST7735(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=SPEED_HZ))
		self.selectAllScreens()
		self.disp.begin()
		self.clearAll()

	def showLogo(self, track, logo):
		# load logo from file to new image object
		image = Image.open(IMG_DIR + logo + '.jpg')
		image = PIL.ImageOps.invert(image)
		#image = image.rotate(0)
		# push image to screen
		self.selectScreen(track)
		self.disp.clear()
		self.disp.display(image)

	def showLogoWithText(self, track, logo, text, textColor):
		# initialize blank canvas then add logo from file
		canvas = Image.new('RGB', WIDTH, HEIGHT)
		logo = Image.open(IMG_DIR + logo + '.jpg')
		logo = PIL.ImageOps.invert(image)
		canvas.paste(logo, (0,0))
		# calculate best-fit font size (by width) and add text
		size = 1
		font = ImageFont.truetype('fonts/verdana.ttf', size)
		while font.getsize(text)[0] < 128:
			size += 1
			font = ImageFont.truetype('fonts/verdana.ttf', size)
		# center vertically
		textHeight = font.getsize(text)[1]
		space = HEIGHT - LOGO_HEIGHT
		margin = (space - textHeight) / 2
		d = ImageDraw.Draw(canvas)
		d.text((-1, LOGO_HEIGHT - 5 + margin), text, font=font, fill=textColor)
		# push image to screen
		self.selectScreen(track)
		self.disp.clear()
		self.disp.display(canvas)

	def clearAll(self):
		self.selectAllScreens()
		self.disp.clear()
		self.disp.display()

	def selectAllScreens(self):
		for p in self.csPins:
			self.gpio.output(p, GPIO.LOW)

	def selectScreen(self, track):
		for p in self.csPins:
			self.gpio.output(p, GPIO.HIGH)
		self.gpio.output(self.csPins[track], GPIO.LOW)
