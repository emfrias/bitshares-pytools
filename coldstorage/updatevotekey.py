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


    raise( "Not working yet!" )


    balance_id     = ""
    privKey        = "" # BTSK7h8z7MHSM6AFEgeEQVupzkH1XRGsKyjd
    newvoteaddress = ""
    votekeyop      = UpdateBalanceVote(balance_id, newvoteaddress, slate_id)
    ops            = []
    ops.append(Operation( "update_balance_vote_op_type", votekeyop ))
    tx             = Transaction( 60*60*12, None, ops )
    sigtx          = SignedTransaction(tx, [privKey])
    return sigtx



    ''' Connect to bitshares client via RPC '''
    rpc = bitsharesrpc.client(args.rpcurl, args.rpcuser, args.rpcpasswd)


if __name__ == '__main__':
    main()
