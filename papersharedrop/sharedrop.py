#!/usr/bin/env python2
import binascii
from pprint import pprint
import json
import sys
import config
import bitsharestools.address as Address
import bitsharestools.transactions as Transaction
import bitsharesrpc
import csv

################################################################################
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
################################################################################
btsprecision       = 1e5  

print( "Connecting to BitShares RPC" )
rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
rpc.wallet_open(config.wallet)
rpc.unlock(999999, config.unlock)

### Withdraw Fee in BTS!
privkeys = []
ops      = []
for bID in config.balanceids :
    print( "Reading BalanceID: %s" % bID )
    balance = rpc.blockchain_get_balance(bID)[ "result" ]

    print( " - Constructing Withdraw operation" )
    if balance["condition"]["asset_id"] is 0 :
        withdraw = Transaction.Withdraw(bID, config.txfee*btsprecision)
    else :
        sharedropamount    = balance["balance"]
        sharedropsymbol    = rpc.blockchain_get_asset(balance["condition"]["asset_id"])["result"]["symbol"]
        sharedropprecision = rpc.blockchain_get_asset(balance["condition"]["asset_id"])["result"]["precision"]
        sharedropassetid   = balance["condition"]["asset_id"]
        withdraw = Transaction.Withdraw(bID, sharedropamount)
    ops.append(Transaction.Operation("withdraw_op_type", withdraw ))
    owner = balance["condition"]["data"]["owner"]
    print( " - Getting private key for signature of owner %s" % owner)
    privkeys.append(rpc.wallet_dump_private_key(owner)["result"])

print "Sharedropping %f %s" % ( sharedropamount/float(sharedropprecision), sharedropsymbol )
amount = sharedropamount/float(sharedropprecision)/float(config.numberpaperwallets)
print "- each %f %s" % ( amount, sharedropsymbol )

print( "Generating %d new addresses for sharedrop" % config.numberpaperwallets )
wifs = []
for didx in xrange( 1, config.numberpaperwallets ) :
    wif     = Address.newwif()
    wifs.append(wif)
    address  = Address.wif2btsaddr(wif)
    print( " - Constructing deposit operation for address %s" % address )
    wst      = Transaction.WithdrawSignatureType( address )
    wc       = Transaction.WithdrawCondition( sharedropassetid, None, "withdraw_signature_type", wst)
    deposit  = Transaction.Deposit( amount, wc )
    ops.append(Transaction.Operation( "deposit_op_type", deposit))

print( "Finalizing Transaction" )
tx       = Transaction.Transaction( 60*60*12, 0, ops )
print( "Signing Transaction" )
sigtx    = Transaction.SignedTransaction(tx, privkeys)

print( "Storing WIF and ADDRESS in wallet.csv backup" )
with open('wallet.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=';')
    for wif in wifs :
        spamwriter.writerow([wif, Address.wif2btsaddr(wif), "%f %s" %(amount,sharedropsymbol), sharedropsymbol])

## Send operation
print( "Broadcasting transaction to the blockchain" )
print( json.dumps( sigtx.tojson(), indent=4 ) )
if query_yes_no( "Please confirm the transaction" ) :
    print( "Transmitting!!" )
    #print(rpc.blockchain_broadcast_transaction(sigtx.tojson()))
else :
    print("blockchain_broadcast_transaction " + str(sigtx.tojson()).replace(' ',''))
