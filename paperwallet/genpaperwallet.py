#!/usr/bin/env python2
import sys
import json
import bitsharestools.address as Address
import bitsharestools.paperwallet as Paper 
import argparse
import os.path

def main() :
    parser = argparse.ArgumentParser(description='Construct a paperwallet and return svg content')
    parser.add_argument('filename', type=str, help='Output file name to store SVG in')
    parser.add_argument('--amount', type=str, help='Text (amount) to be placed on the paper wallet')
    parser.add_argument('--asset', type=str, help='Asset label to be placed on the paper wallet')
    parser.add_argument('--design', type=str, help='Design of the paperwallet (defaults to "cass")')
    parser.add_argument('-encrypt', help='Encrypt private key with BIP38!', action='store_true')
    parser.add_argument('--back_qr', help='Content of the QR-code on the back of the paper wallet', action='store_true')
    parser.add_argument('--back_text1', help='Text field 1 on the back of the paper wallet', action='store_true')
    parser.add_argument('--back_text2', help='Text field 2 on the back of the paper wallet', action='store_true')
    parser.add_argument('--back_text3', help='Text field 3 on the back of the paper wallet', action='store_true')
    parser.set_defaults(design="cass")
    parser.set_defaults(back_text1="Install the BitShares App.", back_text2="Load your funds from the wallet", back_text3="Buy the BitShares 101 Book for $1", back_qr="http://cryptofresh.com/products/8?r=xeroc")
    args = parser.parse_args()

    ''' Generate new wif and address '''
    wif = Address.newwif()
    add = Address.wif2btsaddr(wif)

    ''' Verify that the private keys gives access to address in add '''
    assert Address.priv2btsaddr(Address.wif2hex(wif)) is not add, "private key for address %s is different from given address %s" %(Address.priv2btsaddr(Address.wif2hex(wif)), add) 

    pw = ""
    if args.encrypt :
        import getpass
        while True :
            pw = getpass.getpass('Passphrase: ')
            pwck = getpass.getpass('Retype passphrase: ')
            if(pw == pwck) : 
                break
            else :
                print("Given Passphrases do not match!")

    front,back = Paper.paperwallet(wif, add, args.amount, args.asset, encrypt=pw, design=args.design, backtext1=args.back_text1, backtext2=args.back_text2, backtext3=args.back_text3, backQRcode=args.back_qr)

    extension = os.path.splitext(args.filename)[1]
    if extension == ".svg" :
        open(args.filename, 'wb').write(front)
        open(args.filename.replace('.svg','-back.svg'), 'wb').write(back)
    elif extension == ".pdf" :
        import svg2pdf
        import io
        from PyPDF2 import PdfFileMerger, PdfFileReader
        merger = PdfFileMerger()
        merger.append(PdfFileReader(io.BytesIO(bytes(svg2pdf.svg2pdf(front)))))
        merger.append(PdfFileReader(io.BytesIO(bytes(svg2pdf.svg2pdf(back)))))
        merger.write(args.filename)
    else :
        print("unknown extension %s" % extension)
        return

if __name__ == '__main__':
    main()
