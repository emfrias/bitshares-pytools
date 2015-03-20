#!/usr/bin/env python2
import sys
import json
import bitsharestools.address as Address
import bitsharestools.paperwallet as Paper 
import argparse

def main() :
    parser = argparse.ArgumentParser(description='Construct a paperwallet and store svg file')
    parser.add_argument('filename', type=str, help='Output file name to store SVG in')
    parser.add_argument('--amount', type=str, help='Text (amount) to be placed on the paper wallet')
    parser.add_argument('--asset', type=str, help='Asset label to be placed on the paper wallet')
    parser.add_argument('--design', type=str, help='Design of the paperwallet (defaults to "cass")')
    parser.add_argument('-encrypt', help='Encrypt private key with BIP38!', action='store_true')
    parser.set_defaults(design="cass")
    args = parser.parse_args()

    while True : 
        lines = ""
        try : 
            for line in sys.stdin :
                lines += line
        except (EOFError, KeyboardInterrupt):
            print # end in newline
            sys.exit(1)
            print( lines )
        try :
            j = json.loads(lines)
        except :
            print( "Error parsing JSON!" )
            continue
        break

        if  not "wif_private_key" in j or \
            not "native_address" in j :
            print( "invalid JSON format! Missing native_address and private_key!" )
            continue

    wif = j[ "wif_private_key" ]
    add = j[ "native_address" ]
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

    front,back = Paper.paperwallet(wif, add, args.amount, args.asset, encrypt=pw, design=args.design)

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
