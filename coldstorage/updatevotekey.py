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

try :
    import bitsharestools.address as Address
    import bitsharestools.base58 as b58
    import bitsharestools.bip38 as b38
    import bitsharestools.transactions as Transaction
except ImportError :
    raise ImportError('Error importing bitsharestools')
import argparse

from tools import ask_for_address, ask_for_privkey

def main() :
    parser = argparse.ArgumentParser(description='Offline tool to gather balances in cold storage address')
    parser.add_argument('--voteaddress', type=str, help='address that will be allowed to vote with cold funds instead')
    parser.add_argument('--account', type=str, help='account that will be allowed to vote with cold funds instead')
    parser.add_argument('--rpcurl', type=str, help='')
    parser.add_argument('--rpcuser', type=str, help='')
    parser.add_argument('--rpcpasswd', type=str, help='')
    parser.add_argument('--prefix', type=str, help='defaults to "BTS" (advanced feature)')
    parser.add_argument('--output', type=str, help='filename into which the signed output is stored')
    parser.set_defaults(rpcurl=config.url, rpcuser=config.user, rpcpasswd=config.passwd)
    parser.set_defaults(output="signedtx.txt")
    parser.set_defaults(prefix="BTS")
    args = parser.parse_args()
    PREFIX   = args.prefix
    slate_id = None

    ''' Connect to bitshares client via RPC '''
    rpc = bitsharesrpc.client(args.rpcurl, args.rpcuser, args.rpcpasswd)

    if not args.voteaddress and not args.account :
        print("No voteaddress given! Please specify!")
        args.voteaddress  = ask_for_address() 
    if args.account :
        args.voteaddress  = rpc.wallet_address_create(args.account)[ "result" ]
        print("Using %s from account %s" %(args.voteaddress, args.account))

    ''' Ask for the private key '''
    privkey  = ask_for_privkey()
    address  = Address.priv2btsaddr(Address.wif2hex(privkey))

    ''' balance ids '''
    balances = rpc.blockchain_list_address_balances(address)["result"]
    print("This address holds the following BTS funds (ignoring other assets):")
    ops      = []
    for balance in balances :
        balanceId = balance[0]
        asset_id  = balance[1]["condition"]["asset_id"]
        asset    = rpc.blockchain_get_asset(asset_id)["result"]
        if asset_id == 0 :
            if balance[1]["balance"] == 0: continue
            print("- %f BTS" % ((balance[1]["balance"])/float(asset["precision"])))
            votekeyop      = Transaction.UpdateBalanceVote(balanceId, args.voteaddress, slate_id)
            ops.append(Transaction.Operation( "update_balance_vote_op_type", votekeyop ))

    tx             = Transaction.Transaction( 60*60*12, None, ops )
    sigtx          = Transaction.SignedTransaction(tx, [privkey])

    ''' Store signed transaction '''
    with open(args.output,"wb") as fp :
        fp.write(json.dumps(sigtx.tojson()))
    print("\n%d transaction successfully signed and output written to file '%s'" % (len(ops), args.output) )
    print("To broadcast transaction copy the file and run ./broadcast_signed_tx.py on online computer")

if __name__ == '__main__':
    main()
