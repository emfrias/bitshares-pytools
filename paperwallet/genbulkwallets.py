#!/usr/bin/env python2
import argparse
import os
import csv
import bitsharestools.address as Address
import bitsharestools.paperwallet as Paper 

def main() :
    parser = argparse.ArgumentParser(description='Construct paperwallets according to file')
    parser.add_argument('--design', type=str, help='Design of the paperwallet (defaults to "cass")')
    parser.add_argument('-svg', help='Store as SVG instead of PDF', action='store_true')
    parser.add_argument('wallet', type=str, help='wallet csv file')
    parser.set_defaults(design="cass")
    args = parser.parse_args()

    print( "Constructing paper wallets" )
    with open(args.wallet, 'r') as csvfile:
        spamwriter = csv.reader(csvfile, delimiter=';')
        for wif,add,amount,asset in spamwriter :
            ''' Verify that the private keys gives access to address in add '''
            assert Address.priv2btsaddr(Address.wif2hex(wif)) is not add, "private key for address %s is different from given address %s" %(Address.priv2btsaddr(Address.wif2hex(wif)), add) 
            print("Creating Paperwallet for %s" % (add))
            front,back = Paper.paperwallet(wif, add, amount, asset, design=args.design)
            if args.svg :
                filename = "paperwallets/%s.svg"%add
                open(filename.replace('.svg','-front.svg'), 'wb').write(front)
                open(filename.replace('.svg','-back.svg'), 'wb').write(back)
            else :
                import svg2pdf
                import io
                from PyPDF2 import PdfFileMerger, PdfFileReader
                filename = "paperwallets/%s.pdf"%add
                merger = PdfFileMerger()
                merger.append(PdfFileReader(io.BytesIO(bytes(svg2pdf.svg2pdf(front)))))
                merger.append(PdfFileReader(io.BytesIO(bytes(svg2pdf.svg2pdf(back)))))
                merger.write(filename)
    print( "Done." )

if __name__ == '__main__':
    main()
