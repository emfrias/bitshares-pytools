from PIL import Image
from PIL import ImageFont, ImageDraw
import qrcode
import csv

with open('wallet.csv', 'r') as csvfile:
    spamwriter = csv.reader(csvfile, delimiter=';')
    cnt = 0
    for wif,add in spamwriter :
        cnt+=1
        img = Image.open('02dfed9e_l.png', 'r')
        img_w, img_h = img.size
        
        draw = ImageDraw.Draw(img)
        # draw.textsize(wif)
        #draw.text((228, 445), wif, fill=( 0,0,0,0 ))
        draw.text((228, 445), add, fill=( 0,0,0,0 ))
        draw.text((761, 26), "1 USD", fill=( 0,0,0,0 ))
        img.paste( qrcode.make(wif).resize((180,180)), (998, 27) )
        img.paste( qrcode.make(add).resize((180,180)), (25, 306) )

        #img.show()
        img.save("paperwallet-%03d.png"%cnt, "PNG")
