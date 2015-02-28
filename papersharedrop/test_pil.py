from PIL import Image
from PIL import ImageFont, ImageDraw
import qrcode
import csv

amount_text = "1 USD"

## QR codes
wif_topleft        =  ( 25  , 306 ) 
wif_size           =  ( 180 , 180 ) 
addr_topleft       =  ( 998 , 27  ) 
addr_size          =  ( 180 , 180 ) 

## Text
addt_topleft       =  ( 227 , 445 ) 
addt_bottomright   =  ( 688 , 488 ) 
amount_topleft     =  ( 762 , 26  ) 
amount_bottomright =  ( 974 , 69  ) 

with open('wallet.csv', 'r') as csvfile:
    spamwriter = csv.reader(csvfile, delimiter=';')
    cnt = 0
    for wif,add in spamwriter :
        cnt+=1
        img  = Image.open('paperfront.png', 'r')
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype("Lato-Bold.ttf", 15)

        ## Address
        w,h = draw.textsize(add, font=font)
        x1 = int((addt_topleft[0]+addt_bottomright[0])/2.0 - w/2.0)
        y1 = int((addt_topleft[1]+addt_bottomright[1])/2.0 - h/2.0)
        draw.text(( x1, y1 ), add, fill=( 0,0,0,255 ), font=font)

        ## amount
        w,h = draw.textsize(amount_text, font=font)
        x1 = int((amount_topleft[0]+amount_bottomright[0])/2.0 - w/2.0)
        y1 = int((amount_topleft[1]+amount_bottomright[1])/2.0 - h/2.0)
        draw.text(( x1, y1 ), amount_text, fill=( 0,0,0,255 ), font=font)

        ## QR codes
        img.paste( qrcode.make(wif).resize(addr_size), addr_topleft )
        img.paste( qrcode.make(add).resize(wif_size), wif_topleft )

        #img.show()
        img.save("paperwallet-%03d.png"%cnt, "PNG")
