#!/usr/bin/env python2
import sys
import json
import bitsharestools.address as Address
import bitsharestools.paperwallet as Paper 
import argparse

def main() :
    parser = argparse.ArgumentParser(description='Construct a paperwallet and return svg content')
    parser.add_argument('--amount', type=str, help='text (amount) to be placed on the paper wallet')
    parser.add_argument('--asset', type=str, help='asset label to be placed on the paper wallet')
    parser.add_argument('--design', type=str, help='design of the paperwallet (defaults to "cass")')
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
    print(Paper.paperwallet(wif, add, args.amount, args.asset, args.design))

if __name__ == '__main__':
    main()
