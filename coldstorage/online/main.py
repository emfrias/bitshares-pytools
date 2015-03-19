#!/usr/bin/env python2
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

''' Get available funds from bitshares rpc '''
def get_available_balances(rpc, address):
    balances = []
    for b in rpc.blockchain_list_address_balances(address)["result"] :
        asset_id = b[1]["condition"]["asset_id"]
        asset    = rpc.blockchain_get_asset(asset_id)["result"]
        balances.append( {
                "balanceid" : b[0],
                "balance"   : (b[1]["balance"])/float(asset["precision"]),
                "symbol"    : asset["symbol"],
                "asset_id"  : asset["id"],
                "precision" : asset["precision"],
                "owner"     : b[1]["condition"]["data"]["owner"]
            })
    return balances

def main() :
    parser = argparse.ArgumentParser(description='Offline tool to gather balances in cold storage address')
    parser.add_argument('coldaddress', type=str, help='cold storage address to get funds from (required)')
    parser.add_argument('--filename', type=str, help='filename in which to store the available funds')
    parser.add_argument('--rpcurl', type=str, help='')
    parser.add_argument('--rpcuser', type=str, help='')
    parser.add_argument('--rpcpasswd', type=str, help='')
    parser.set_defaults(rpcurl=config.url, rpcuser=config.user, rpcpasswd=config.passwd)
    parser.set_defaults(filename="availablefunds.txt")
    args = parser.parse_args()

    ''' Connect to bitshares client via RPC '''
    rpc = bitsharesrpc.client(args.rpcurl, args.rpcuser, args.rpcpasswd)

    ''' Get available funds '''
    balances  = get_available_balances(rpc, args.coldaddress)

    ''' Format for transfer '''
    print("Available Funds in cold storage address %s:" % args.coldaddress)
    funds = []
    for t in balances :
        funds.append("%f ; %s ; %d ; %d ; %s ; %s\n" %(t["balance"],t["symbol"],t["asset_id"],t["precision"],t["balanceid"],t["owner"]))
        print("- %f %s" %( t[ "balance" ], t[ "symbol" ]))

    with open(args.filename, "w") as fp :
        fp.write(str("".join(funds)))

    print( "Stored funds for %d assets in '%s' for offline construction & signing." % (len(funds), args.filename) )

if __name__ == '__main__':
    main()
