#!/usr/bin/env python2
import binascii
import Transactions
from pprint import pprint
import json
import bitsharesrpc
import config

withdrawals = [
            {
                "balance_id":"BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh",
                "privkey"   :"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "amount"    : .1 * 1e5,
                "asset_id"  : 0
            },
            {
                "balance_id":"BTSG9SrG1qe2EtDbJkjbTUN4epSNG755P1y7",
                "privkey"   :"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "amount"    : 5*1e4,
                "asset_id"  : 21
            },
       ] 

receiveAddresses = [ 
        {
            "address" : "BTS8kXVZ6o1uZDnCkUaKgKVUaytFSFespzWm",
            "amount"  : 1.0 * 1e4,
            "asset_id": 21
        },
        {
            "address" : "BTS9NArckpAesJLQVJP42yzpp1D7RahyjaL7",
            "amount"  : 1.0 * 1e4,
            "asset_id": 21
        },
        {
            "address" : "BTSFweqCSFv2seFPsLxjp6eWXwCkN66uxesx",
            "amount"  : 1.0 * 1e4,
            "asset_id": 21
        },
        {
            "address" : "BTSNtJPSq8ejj9CtBK5YnkVKEBxmXK5TZW12",
            "amount"  : 1.0 * 1e4,
            "asset_id": 21
        },
        {
            "address" : "BTS22qUEF6TT5yL7SwkvU4hdMtK2zZEAGmeZ",
            "amount"  : 1.0 * 1e4,
            "asset_id": 21
        },
        ]
otk            = None
slate_id       = None

ops      = []
privkeys = []
### Withdraw Fee in BTS!
for w in withdrawals :
    withdraw = Transactions.Withdraw( w["balance_id"], w["amount"])
    ops.append(Transactions.Operation( "withdraw_op_type", withdraw ))
    privkeys.append(w["privkey"])

for d in receiveAddresses :
    wst      = Transactions.WithdrawSignatureType( d[ "address" ] )
    wc       = Transactions.WithdrawCondition( d["asset_id"], slate_id, "withdraw_signature_type", wst)
    deposit  = Transactions.Deposit( d["amount"], wc )
    ops.append(Transactions.Operation( "deposit_op_type", deposit))

tx       = Transactions.Transaction( 60*60*12, 0, ops )
sigtx    = Transactions.SignedTransaction(tx, privkeys)

print( json.dumps( sigtx.tojson(  ), sort_keys=True, indent=4 ) )
print(binascii.hexlify( sigtx.towire(  ) ))

## Send operation
print "="*80
rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
print(rpc.blockchain_broadcast_transaction(sigtx.tojson()))
