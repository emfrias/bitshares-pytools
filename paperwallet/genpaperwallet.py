#!/usr/bin/env python2
import sys
import json
import bitsharestools.address as Address
import bitsharestools.paperwallet as Paper 
import argparse

def main() :
    parser = argparse.ArgumentParser(description='Construct a paperwallet and return svg content')
    parser.add_argument('filename', type=str, help='Output file name to store SVG in')
    parser.add_argument('--amount', type=str, help='Text (amount) to be placed on the paper wallet')
    parser.add_argument('--asset', type=str, help='Asset label to be placed on the paper wallet')
    parser.add_argument('--design', type=str, help='Design of the paperwallet (defaults to "cass")')
    parser.add_argument('-encrypt', help='Encrypt private key with BIP38!', action='store_true')
    parser.set_defaults(design="cass")
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

    svg = (Paper.paperwallet(wif, add, args.amount, args.asset, encrypt=pw, design=args.design))
    open(args.filename, 'wb').write(svg)

if __name__ == '__main__':
    main()
