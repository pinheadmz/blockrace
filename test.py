from PIL import Image, ImageDraw, ImageFont
WIDTH = 128
HEIGHT = 160
SPEED_HZ = 4000000
IMG_DIR = '/home/pi/blockrace/jpg128/'
LOGO_HEIGHT = 128

i = Image.open('jpg128/bitcoin.jpg')

j = Image.new('RGB', (128, 160))

j.paste(i,(0,0))

size = 10

text = "Ethereum Classic"

font = ImageFont.truetype('fonts/verdana.ttf', size)

while font.getsize(text)[0] < 128:
	size += 1
	font = ImageFont.truetype('fonts/verdana.ttf', size)

d=ImageDraw.Draw(j)
textHeight = font.getsize(text)[1]
space = HEIGHT - LOGO_HEIGHT
margin = (space - textHeight) / 2
d = ImageDraw.Draw(j)
d.text((-1, LOGO_HEIGHT - 5 + margin), text, font=font, fill=(255,255,255))
j.show()