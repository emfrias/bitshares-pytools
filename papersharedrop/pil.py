from PIL import Image
from PIL import ImageFont, ImageDraw
import qrcode
 

img = Image.open('02dfed9e_l.png', 'r')
img_w, img_h = img.size
 
draw = ImageDraw.Draw(img)
draw.text((10, 15), "Hello")
draw.text((10, 25), "world")

qr = qrcode.make('Some data here')

img.paste( qr, (20, 30) )
img.show()

