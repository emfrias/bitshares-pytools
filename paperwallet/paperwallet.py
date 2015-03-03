#!/usr/bin/env python2
import binascii
from pprint import pprint
import json
import sys
import csv
import qrcode
import qrcode.image.svg
from xml.dom import minidom
#import xml.etree.cElementTree as et
import lxml.etree as et

print( "Constructing paper wallets" )
amount_text = "$50c"
svgfile     = "paperfront.svg"

with open('wallet.csv', 'r') as csvfile:
    spamwriter = csv.reader(csvfile, delimiter=';')
    cnt = 0
    for wif,add in spamwriter :
        dom   = et.parse(open(svgfile,'r'))
        root  = dom.getroot()
        for layer in root.findall("./{http://www.w3.org/2000/svg}g") :
            ## QRcode address
            qr = qrcode.make(add, image_factory=qrcode.image.svg.SvgPathImage)
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "QRaddress" :
                x = float(layer.find("{http://www.w3.org/2000/svg}rect").get("x"))
                y = float(layer.find("{http://www.w3.org/2000/svg}rect").get("y"))
                scale = 1.0
                layer.set("transform","translate(%f,%f) scale(%f)" % (x,y,scale))
                layer.append(qr.make_path())
                layer.remove(layer.find("{http://www.w3.org/2000/svg}rect"))
            ## QRcode privkey
            qr = qrcode.make(wif, image_factory=qrcode.image.svg.SvgPathImage)
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "QRprivkey" :
                x = float(layer.find("{http://www.w3.org/2000/svg}rect").get("x"))
                y = float(layer.find("{http://www.w3.org/2000/svg}rect").get("y"))
                scale = 1.0
                layer.set("transform","translate(%f,%f) scale(%f)" % (x,y,scale))
                layer.append(qr.make_path())
                layer.remove(layer.find("{http://www.w3.org/2000/svg}rect"))

            ## Address
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "textamount" :
                layer.find("{http://www.w3.org/2000/svg}text").text = amount_text
            ## amount
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "textaddress" :
                layer.find("{http://www.w3.org/2000/svg}text").text = add
        dom.write("paperwallets/%s.svg" % add)
print( "Done." )
