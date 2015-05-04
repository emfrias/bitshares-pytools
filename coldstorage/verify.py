#!/usr/bin/env python2
import json
import sys
import argparse

try :
    import bitsharestools.address as Address
    import bitsharestools.base58 as b58
    import bitsharestools.bip38 as b38
    import bitsharestools.transactions as Transaction
except ImportError :
    raise ImportError('Module bitsharestools missing')

from tools import ask_for_privkey

def main() :
    ''' Ask for the private key '''
    privkey, address = ask_for_privkey()
    print("Private key gives access to address: %s" % ( address) )

if __name__ == '__main__':
    main()
