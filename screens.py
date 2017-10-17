from PIL import Image
import PIL.ImageOps
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import time


WIDTH = 128
HEIGHT = 160
SPEED_HZ = 4000000
IMG_DIR = '/home/pi/blockrace/jpg128/'

# Raspberry Pi configuration.
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

	def showLogo(self, s, logo):
		image = Image.open(IMG_DIR + logo + '.jpg')
		image = PIL.ImageOps.invert(image)
		image = image.rotate(270)
		self.selectScreen(s)
		self.disp.clear()
		self.disp.display(image)

	def clearAll(self):
		self.selectAllScreens()
		self.disp.clear()
		self.disp.display()

	def selectAllScreens(self):
		for p in self.csPins:
			self.gpio.output(p, GPIO.LOW)

	def selectScreen(self, s):
		s -= 1
		for p in self.csPins:
			self.gpio.output(p, GPIO.HIGH)
		self.gpio.output(self.csPins[s], GPIO.LOW)
