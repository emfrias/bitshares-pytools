#!/usr/bin/env python2
import sys
import config
import bitsharesrpc
import argparse

def get_available_balances(rpc, address):
    balances = []
    for b in rpc.blockchain_list_address_balances(address)["result"] :
        asset_id = b[1]["condition"]["asset_id"]
        asset = rpc.blockchain_get_asset(asset_id)["result"]
        balances.append( {
                "balanceid" : b[0],
                "balance" : (b[1]["balance"])/float(asset["precision"]),
                "symbol" : asset["symbol"],
                "asset_id" : asset[ "id" ],
                "precision" : asset[ "precision" ],
                "owner" : b[1]["condition"]["data"]["owner"]
            })
    return balances

def main() :
    parser = argparse.ArgumentParser(description='Offline tool to gather balances in cold storage address')
    parser.add_argument('--filename', type=str, help='filename in which to store the available funds')
    parser.add_argument('--address', type=str, help='cold storage address')
    parser.add_argument('--rpcurl', type=str, help='')
    parser.add_argument('--rpcuser', type=str, help='')
    parser.add_argument('--rpcpasswd', type=str, help='')
    parser.set_defaults(rpcurl=config.url, rpcuser=config.user, rpcpasswd=config.passwd)
    parser.set_defaults(filename="availablefunds.txt", address=config.coldaddress)
    args = parser.parse_args()

    print( "Connecting to BitShares RPC" )
    rpc = bitsharesrpc.client(args.rpcurl, args.rpcuser, args.rpcpasswd)
    balances  = get_available_balances(rpc, args.address)
    ''' Format for transfer '''
    print( "Available Funds" )
    txt = ""
    for t in balances :
        txt += ("%f ; %s ; %d ; %d ; %s ; %s\n" %(t["balance"],t["symbol"],t["asset_id"],t["precision"],t["balanceid"],t["owner"]))
        print( "%f %s" %( t[ "balance" ], t[ "symbol" ] ) )

    with open( args.filename,"w" ) as fp :
        fp.write(str(txt))
    print( "Stored in file %s (for offline tools)" % args.filename )

if __name__ == '__main__':
    main()
