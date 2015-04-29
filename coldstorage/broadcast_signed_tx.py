#!/usr/bin/env python2
import json
import sys
try :
    import config
except ImportError :
    raise ImportError('Configuration file "config.py" missing. See "config-example.py"!')

try :
    import bitsharesrpc
except ImportError :
    raise ImportError('Python package "bitsharesrpc" missing! Read the README in the main repository directory!')
import argparse

def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def main() :
    parser = argparse.ArgumentParser(description='Broadcast signed transaction to the network!')
    parser.add_argument('--filename', type=str, help='File containing the signed transaction')
    parser.add_argument('--rpcurl', type=str, help='')
    parser.add_argument('--rpcuser', type=str, help='')
    parser.add_argument('--rpcpasswd', type=str, help='')
    parser.set_defaults(rpcurl=config.url, rpcuser=config.user, rpcpasswd=config.passwd)
    parser.set_defaults(filename="signedtx.txt")
    args = parser.parse_args()

    ''' Connect to bitshares client via RPC '''
    rpc = bitsharesrpc.client(args.rpcurl, args.rpcuser, args.rpcpasswd)

    print( "Broadcasting transaction:" )
    with open( args.filename, "r" ) as f :
        js = json.loads(f.read())
        print( json.dumps(js, indent=4) )
        if query_yes_no("Are you sure?") :
            print(rpc.blockchain_broadcast_transaction(js))

if __name__ == '__main__':
    main()
