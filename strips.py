import time
import random
from neopixel import *

# constants
NUM_TRACKS = 4
TRACK_LENGTH = 75
# speed of blocks mode target based on coin interval
TARGET_BLOCK_COUNT = 8
BRIGHTNESS_NOTCH = 5
MIN_BRIGHTNESS = 1
MAX_BRIGHTNESS = 100
# means % up or down that fills half strip from center out
PRICE_CHANGE_RANGE = 5
NUM_DROPLETS = 4

# LED strip configuration:
LED_COUNT      = 300      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

class Strips():
	def __init__(self):
		# Create NeoPixel object with appropriate configuration.
		self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
		# Intialize the library (must be called once before other functions).
		self.strip.begin()
		self.allOff()
		# init variables for frame iteration
		# for twinkle
		self.randBrightness = [random.randint(MIN_BRIGHTNESS, MAX_BRIGHTNESS) for x in range(TRACK_LENGTH * NUM_TRACKS)]
		self.brightnessDirection = [random.choice([-1,1]) for x in range(TRACK_LENGTH * NUM_TRACKS)]
		# for price
		self.dropletPos = 0

	# all lights off
	def allOff(self):
		for i in range(self.strip.numPixels()):
			self.strip.setPixelColor(i, Color(0,0,0))
		self.strip.show()

	# set range to one solid color
	def stripe(self, start, end, color):
		for i in range(start, end):
			self.strip.setPixelColor(i, Color(*color))

	# set track to one color with random brightnesses for twinkle effect
	def twinkle(self, track, color):
		for i in range (track * TRACK_LENGTH, track * TRACK_LENGTH + TRACK_LENGTH):
			# modulate brightness slowly between frames
			if self.randBrightness[i] >= MAX_BRIGHTNESS - BRIGHTNESS_NOTCH:
				self.brightnessDirection[i] = -1
			if self.randBrightness[i] <= MIN_BRIGHTNESS + BRIGHTNESS_NOTCH:
				self.brightnessDirection[i] = 1
			self.randBrightness[i] += (self.brightnessDirection[i] * BRIGHTNESS_NOTCH)
			self.strip.setPixelColor(i, Color(*tuple(int(x * self.randBrightness[i] / MAX_BRIGHTNESS) for x in color)))

	# light specific dots in a track to one color
	def blocks(self, track, color, interval, history):
		# based on speed of coin, tune the speed of the dots
		dotInterval = TRACK_LENGTH / TARGET_BLOCK_COUNT
		dotTime = interval / dotInterval
		trackTime = dotTime * (TRACK_LENGTH - 1)
		now = int(time.time())

		# construct dot pattern from chain history
		pattern = []
		tip = -1
		while now - history[tip].time <= trackTime:
			timeSince = now - history[tip].time
			pattern.append(timeSince / dotTime)
			tip -= 1
			if tip * -1 > len(history):
				break

		# set background color then add bright dots
		for i in range (track * TRACK_LENGTH, track * TRACK_LENGTH + TRACK_LENGTH):
			brightness = 0.05
			bgColor = tuple(int(x * brightness) for x in color)
			self.strip.setPixelColor(i, Color(*bgColor))
		for j in pattern:
			self.strip.setPixelColor(track * TRACK_LENGTH + j, Color(*color))

	# indicate price change
	def price(self, track, dayPriceChange):
		# TODO: animate droplets in direction of change
		# TODO: color layers for big changes!
		dayPriceChange = float(dayPriceChange)
		center = TRACK_LENGTH / 2
		dotsPerPct = center / PRICE_CHANGE_RANGE
		# num LEDs to represent price, might be negative!
		dotsOn = int(dotsPerPct * dayPriceChange)
		color = Color(255,0,0) if dayPriceChange < 0 else Color(0,255,0)
		# blank out strip first
		self.stripe(track * TRACK_LENGTH, (track * TRACK_LENGTH) + TRACK_LENGTH, (0,0,0))
		# draw the meter
		for i in range (min(center+dotsOn, center), max(center+dotsOn, center)):
			dot = (track * TRACK_LENGTH) + i
			self.strip.setPixelColor(dot, color)
		# draw the droplets
		dropSpace = center / NUM_DROPLETS
		for j in range(NUM_DROPLETS):
			direction = -1 if dayPriceChange < 0 else 1
			dropDotPos = (track * TRACK_LENGTH) + center + (direction * ((j * dropSpace) + self.dropletPos))
			newColor = color if self.strip.getPixelColor(dot) == Color(0,0,0) else Color(0,0,0)
			self.strip.setPixelColor(dropDotPos, newColor)
		self.dropletPos = (self.dropletPos + 1) % dropSpace

'''
# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=5):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
	"""Movie theater light style chaser animation."""
	for j in range(iterations):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, color)
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
	"""Draw rainbow that fades across all pixels at once."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((i+j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
	"""Rainbow movie theater light style chaser animation."""
	for j in range(256):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, wheel((i+j) % 255))
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)
'''
