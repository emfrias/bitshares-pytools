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
from PIL import Image
from PIL import ImageFont, ImageDraw
import qrcode

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
        spamwriter.writerow([wif, Address.wif2btsaddr(wif)])

## Send operation
print( "Broadcasting transaction to the blockchain" )
print( json.dumps( sigtx.tojson(), indent=4 ) )
if query_yes_no( "Please confirm the transaction" ) :
    print( "Transmitting!!" )
    #print(rpc.blockchain_broadcast_transaction(sigtx.tojson()))


print( "Constructing paper wallets" )
## QR codes
wif_topleft        =  ( 25  , 306 ) 
wif_size           =  ( 180 , 180 ) 
addr_topleft       =  ( 998 , 27  ) 
addr_size          =  ( 180 , 180 ) 

## Text
addt_topleft       =  ( 227 , 445 ) 
addt_bottomright   =  ( 688 , 488 ) 
amount_topleft     =  ( 762 , 26  ) 
amount_bottomright =  ( 974 , 69  ) 

amount_text = "%.2f %s" % ( amount, sharedropsymbol )

cnt = 0
for wif in wifs :
    add = Address.wif2btsaddr(wif)
    img  = Image.open('paperfront.png', 'r')
    draw = ImageDraw.Draw(img)

    ## Address
    w,h = draw.textsize(add)
    x1 = int((addt_topleft[0]+addt_bottomright[0])/2.0 - w/2.0)
    y1 = int((addt_topleft[1]+addt_bottomright[1])/2.0 - h/2.0)
    draw.text(( x1, y1 ), add, fill=( 0,0,0,0 ))

    ## amount
    w,h = draw.textsize(amount_text)
    x1 = int((amount_topleft[0]+amount_bottomright[0])/2.0 - w/2.0)
    y1 = int((amount_topleft[1]+amount_bottomright[1])/2.0 - h/2.0)
    draw.text(( x1, y1 ), amount_text, fill=( 0,0,0,0 ))

    ## QR codes
    img.paste( qrcode.make(wif).resize(addr_size), addr_topleft )
    img.paste( qrcode.make(add).resize(wif_size), wif_topleft )

    #img.show()
    cnt+=1
    img.save("paperwallet-%03d.png"%cnt, "PNG")

print( "Done." )
