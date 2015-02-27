#!/usr/bin/env python2
import binascii
from pprint import pprint
import json
import config
import bitsharestools.address as Address
import bitsharestools.transactions as Transaction
import bitsharesrpc
import csv

## Balance IDs ( DO NOT MIX THIS WITH ADDRESSES )
balanceids = [
                "BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh",   # BTS for fees
                "BTSG9SrG1qe2EtDbJkjbTUN4epSNG755P1y7",  # USD to sharedrop
              ] 

numberpaperwallets = 10
txfee = 0.5 # BTS
btsprecision = 1e5

################################################################################
rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
rpc.wallet_open(config.wallet)
rpc.unlock(999999, config.unlock)

### Withdraw Fee in BTS!
privkeys = []
ops      = []
for bID in balanceids :
    balance = rpc.blockchain_get_balance(bID)[ "result" ]

    if balance["condition"]["asset_id"] is 0 :
        withdraw = Transaction.Withdraw(bID, txfee*btsprecision)
    else :
        sharedropamount    = balance["balance"]
        sharedropsymbol    = rpc.blockchain_get_asset(balance["condition"]["asset_id"])["result"]["symbol"]
        sharedropprecision = rpc.blockchain_get_asset(balance["condition"]["asset_id"])["result"]["precision"]
        sharedropassetid   = balance["condition"]["asset_id"]
        withdraw = Transaction.Withdraw(bID, sharedropamount)
    ops.append(Transaction.Operation("withdraw_op_type", withdraw ))
    # get private key
    owner = balance["condition"]["data"]["owner"]
    privkeys.append(rpc.wallet_dump_private_key(owner)["result"])

print "Sharedropping %f %s" % ( sharedropamount/float(sharedropprecision), sharedropsymbol )
amount = sharedropamount/float(sharedropprecision)/float(numberpaperwallets)
print "- each %f %s" % ( amount, sharedropsymbol )

wifs = []
for didx in xrange( 1, numberpaperwallets ) :
    wif     = Address.newwif()
    wifs.append(wif)
    address  = Address.wif2btsaddr(wif)
    wst      = Transaction.WithdrawSignatureType( address )
    wc       = Transaction.WithdrawCondition( sharedropassetid, None, "withdraw_signature_type", wst)
    deposit  = Transaction.Deposit( amount, wc )
    ops.append(Transaction.Operation( "deposit_op_type", deposit))

tx       = Transaction.Transaction( 60*60*12, 0, ops )
sigtx    = Transaction.SignedTransaction(tx, privkeys)

#print( json.dumps( sigtx.tojson(  ), sort_keys=True, indent=4 ) )
#print(binascii.hexlify( sigtx.towire(  ) ))

with open('wallet.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=';')
    for wif in wifs :
        spamwriter.writerow([wif, Address.wif2btsaddr(wif)])

# ## Send operation
# #print "="*80
# #print(rpc.blockchain_broadcast_transaction(sigtx.tojson()))
