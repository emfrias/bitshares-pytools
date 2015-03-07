#!/usr/bin/env python2
import csv
import qrcode
import qrcode.image.svg
import lxml.etree as et
from copy import deepcopy

print( "Constructing paper wallets" )
svgfile     = "paperwallet-front.svg"

with open('wallet.csv', 'r') as csvfile:
    spamwriter = csv.reader(csvfile, delimiter=';')
    cnt = 0
    for wif,add,amount,asset in spamwriter :
        print("Creating Paperwallet for %s" % add)
        dom   = et.parse(open(svgfile,'r'))
        root  = dom.getroot()
        for layer in root.findall("./{http://www.w3.org/2000/svg}g") :
            ## QRcode address
            qr = qrcode.make(add, image_factory=qrcode.image.svg.SvgPathImage)
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "QRaddress" :
                x = float(layer.find("{http://www.w3.org/2000/svg}rect").get("x"))
                y = float(layer.find("{http://www.w3.org/2000/svg}rect").get("y"))
                scale = float(layer.find("{http://www.w3.org/2000/svg}rect").get("width"))/(qr.width+2*qr.border)
                layer.set("transform","translate(%f,%f) scale(%f)" % (x,y,scale))
                layer.append(qr.make_path())
                layer.remove(layer.find("{http://www.w3.org/2000/svg}rect"))
            ## QRcode privkey
            qr = qrcode.make(wif, image_factory=qrcode.image.svg.SvgPathImage)
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "QRprivkey" :
                x = float(layer.find("{http://www.w3.org/2000/svg}rect").get("x"))
                y = float(layer.find("{http://www.w3.org/2000/svg}rect").get("y"))
                scale = float(layer.find("{http://www.w3.org/2000/svg}rect").get("width"))/(qr.width+2*qr.border)
                layer.set("transform","translate(%f,%f) scale(%f)" % (x,y,scale))
                layer.append(qr.make_path())
                layer.remove(layer.find("{http://www.w3.org/2000/svg}rect"))
            ## Address
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "textamount" :
                layer.find("{http://www.w3.org/2000/svg}text").find("{http://www.w3.org/2000/svg}tspan").text = amount
            ## amount
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "textaddress" :
                layer.find("{http://www.w3.org/2000/svg}text").find("{http://www.w3.org/2000/svg}tspan").text = add
            ## Asset logo
            assetfile = "BitAssets/bit%s-accepted-flat-square-2.svg" % asset.upper()
            assetlogodom   = et.parse(open(assetfile,'r'))
            assetlogoroot  = assetlogodom.getroot()
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "assetlogo" :
                x = float(layer.find("{http://www.w3.org/2000/svg}rect").get("x"))
                y = float(layer.find("{http://www.w3.org/2000/svg}rect").get("y"))
                scale = float(layer.find("{http://www.w3.org/2000/svg}rect").get("width"))/float(assetlogoroot.get("width").split("px")[0])
                layer.set("transform","translate(%f,%f) scale(%f)" % (x,y,scale))
                layer.append(deepcopy(assetlogoroot))
                layer.remove(layer.find("{http://www.w3.org/2000/svg}rect"))
        dom.write("paperwallets/%s.svg" % add)
print( "Done." )
