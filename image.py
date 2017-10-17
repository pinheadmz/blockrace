from PIL import Image
import PIL.ImageOps
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import time


WIDTH = 128
HEIGHT = 160
SPEED_HZ = 4000000


# Raspberry Pi configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

# Create TFT LCD display class.
disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev(
        SPI_PORT,
        SPI_DEVICE,
        max_speed_hz=SPEED_HZ))

# Load an image.
print('Loading image...')
image1 = Image.open('/home/pi/blockrace/jpg128/bitcoin.jpg')
image2 = Image.open('/home/pi/blockrace/jpg128/decred.jpg')
image3 = Image.open('/home/pi/blockrace/jpg128/monero.jpg')


image1 = PIL.ImageOps.invert(image1)
image2 = PIL.ImageOps.invert(image2)
image3 = PIL.ImageOps.invert(image3)


# Resize the image and rotate it so matches the display.
#image1 = image1.rotate(90).resize((WIDTH, HEIGHT))
#image2 = image2.rotate(90).resize((WIDTH, HEIGHT))
#image3 = image3.rotate(90).resize((WIDTH, HEIGHT))
image1 = image1.rotate(270)
image2 = image2.rotate(270)
image3 = image3.rotate(270)

# Draw the image on the display hardware.
print('Drawing images')

pins = GPIO.get_platform_gpio()
pins.setup(14, GPIO.OUT)
pins.setup(15, GPIO.OUT)
pins.setup(23, GPIO.OUT)


# Initialize display.
pins.output(14, GPIO.LOW)
pins.output(15, GPIO.LOW)
pins.output(23, GPIO.LOW)
disp.begin()

print("1")
pins.output(14, GPIO.LOW)
pins.output(15, GPIO.HIGH)
pins.output(23, GPIO.HIGH)
disp.clear()
disp.display(image1)

print("2")
pins.output(14, GPIO.HIGH)
pins.output(15, GPIO.LOW)
pins.output(23, GPIO.HIGH)
disp.clear()
disp.display(image2)

print("3")
pins.output(14, GPIO.HIGH)
pins.output(15, GPIO.HIGH)
pins.output(23, GPIO.LOW)
disp.clear()
disp.display(image3)

time.sleep(5)
pins.output(14, GPIO.LOW)
pins.output(15, GPIO.LOW)
pins.output(23, GPIO.LOW)
disp.clear()
disp.display()
