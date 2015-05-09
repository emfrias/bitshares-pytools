#!/usr/bin/env python2
import sys
import json

try :
    import config
except ImportError :
    raise ImportError('Configuration file "config.py" missing. See "config-example.py"!')
try :
    import bitsharesrpc
except ImportError :
    raise ImportError('Python package "bitsharesrpc" missing! Read the README in the main repository directory!')

import argparse

#from tools import ask_for_address, ask_for_privkey

def main() :
    parser = argparse.ArgumentParser(description='Tool for updating votes from vote_only keys. The votes have to be defined using the (GUI) client.')
    #parser.add_argument('addresses', nargs='+', type=str, help='coldaddresses with BTS for which to update the vote')
    parser.add_argument('--rpcurl', type=str, help='')
    parser.add_argument('--rpcuser', type=str, help='')
    parser.add_argument('--rpcpasswd', type=str, help='')
    parser.add_argument('--prefix', type=str, help='defaults to "BTS" (advanced feature)')
    parser.set_defaults(rpcurl=config.url, rpcuser=config.user, rpcpasswd=config.passwd)
    #parser.set_defaults(addresses=config.coldaddresses)
    parser.set_defaults(prefix="BTS")
    args = parser.parse_args()
    PREFIX   = args.prefix

    ''' Connect to bitshares client via RPC '''
    print( "Opening connection to client" )
    rpc = bitsharesrpc.client(args.rpcurl, args.rpcuser, args.rpcpasswd)
    print( "Opening wallet %s" % config.wallet )
    ret = rpc.wallet_open(config.wallet)
    print( "Unlocking wallet" )
    ret = rpc.unlock(999999, config.unlock)

    ''' Gather balanceids from the blockchain corresponding to the cold addresses '''
    #for address in args.addresses :
    for address in config.coldaddresses :
        balances = rpc.blockchain_list_address_balances(address)["result"]
        print("Updating votes for address %s:" % (address))
        for balance in balances :
            balanceId = balance[0]
            asset_id  = balance[1]["condition"]["asset_id"]
            asset    = rpc.blockchain_get_asset(asset_id)["result"]
            if asset_id == 0 :
                if balance[1]["balance"] == 0: continue
                print("- %f BTS" % ((balance[1]["balance"])/float(asset["precision"])))
                rpc.wallet_balance_set_vote_info(balanceId, "", "vote_recommended")
    rpc.lock()

if __name__ == '__main__':
    main()
