#!/usr/bin/env python2
from pprint import pprint
import json
import sys
import config
import bitsharestools.address as Address
import bitsharestools.transactions as Transaction
import bitsharesrpc
import csv
import argparse
import binascii

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

def main() : 
    parser = argparse.ArgumentParser(description='Construct paperwallets according to file')
    parser.add_argument('fromaddress', type=str, help='Address to take funds from')
    parser.add_argument('number', type=int, help='Number of sharedrop addresses to create')
    parser.add_argument('fundwith', nargs='+', type=str, help='Fund to send to each address')
    parser.add_argument('--displayprecision', type=str, help='Display precision for paper wallet')
    parser.add_argument('--txfee', type=str, help='Transaction fee')
    parser.add_argument('--rpcurl', type=str, help='')
    parser.add_argument('--rpcuser', type=str, help='')
    parser.add_argument('--rpcpasswd', type=str, help='')
    parser.add_argument('--wallet', type=str, help='')
    parser.add_argument('--unlock', type=str, help='')
    parser.add_argument('--filename', type=str, help='')
    parser.add_argument('--account', help='user keys linked to account')
    parser.set_defaults(rpcurl=config.url, rpcuser=config.user, rpcpasswd=config.passwd, wallet=config.wallet, unlock=config.unlock, txfee=config.txfee, displayprecision=2, filename="sharedrop-signed-transaction.txt")
    args = parser.parse_args()

    ''' Connect to bitshares client via RPC '''
    rpc = bitsharesrpc.client(args.rpcurl, args.rpcuser, args.rpcpasswd)
    rpc.wallet_open(args.wallet)
    rpc.unlock(999999, args.unlock)

    ###
    print("Assets for sharedrop into each address:")
    fundwith = {}
    sharedroptext = ""
    for fund in args.fundwith :
        try :
            amount,symbol = str(fund).split(" ")
            amount = float(amount)
            asset = rpc.blockchain_get_asset(symbol)['result']
            assert asset is not None, "Asset %s does not exist on the blockchain" % symbol
        except :
            print("Something went wrong when loading 'fundwith'.")
            parser.print_usage()
            raise
        fundwith[symbol] = amount*asset["precision"]
        sharedroptext += "%.*f%s " % (args.displayprecision, amount, symbol)
        print(" + %f %s" % (amount, symbol))

    ### Withdraw Fee in BTS!
    have     = {}
    print("Getting balance from given address")
    balanceids = rpc.blockchain_list_address_balances(args.fromaddress)['result']
    for bIDobj in balanceids :
        bID       = bIDobj[0]
        balance   = bIDobj[1]
        if symbol == "BTS" : ## Substract TX fee right away
            balance["balance"] -= int( float(args.txfee) * 1e5)
        asset_id  = balance["condition"]["asset_id"]
        asset     = rpc.blockchain_get_asset(asset_id)["result"]
        precision = float(asset["precision"])
        amount    = int(balance["balance"])
        symbol    = asset["symbol"]
        have[symbol] = [amount, bIDobj, asset]

    ''' Check if enough funded '''
    for symbol in fundwith.keys() : 
        if symbol in have :
            amount = have[ symbol ][ 0 ]
            if fundwith[symbol] * args.number > amount :
                raise Exception("Not enough funds. Need %f %s, but only have %f %s" %(fundwith[symbol]*args.number, symbol, amount, symbol))
        else : 
            raise Exception("Missing asset %s in address." % symbol)

    privkeys = []
    ops      = []
    print( "Constructing Withdraw operations" )
    for symbol in fundwith.keys() :
        bIDobj    = have[symbol][1]
        asset     = have[symbol][2]
        bID       = bIDobj[0]
        balance   = bIDobj[1]
        asset_id  = asset["id"]
        precision = float(asset["precision"])
        amount    = fundwith[symbol] * args.number
        if symbol == "BTS" :
            amount += float(args.txfee) * 1e5
        ops.append(Transaction.Operation("withdraw_op_type", Transaction.Withdraw(bID, amount) ))
        owner = balance["condition"]["data"]["owner"]
        privkeys.append(rpc.wallet_dump_private_key(owner)["result"])

    ''' Ensure that TX fee is paied '''
    if "BTS" not in fundwith : 
        symbol = "BTS"
        print( "Enforcing TX fee" )
        if symbol in have :
            if have[symbol] < float(args.txfee) * 1e5 :
                raise Exception("Not enough funds. Need %f %s, but only have %f %s" %( float(args.txfee), symbol, have[symbol], symbol))
        else : 
            raise Exception("Missing asset %s in address." % symbol)
        bIDobj    = have[symbol][1]
        asset     = have[symbol][2]
        bID       = bIDobj[0]
        balance   = bIDobj[1]
        asset_id  = asset["id"]
        precision = float(asset["precision"])
        amount    = float(args.txfee) * precision
        ops.append(Transaction.Operation("withdraw_op_type", Transaction.Withdraw(bID, amount) ))
        owner = balance["condition"]["data"]["owner"]
        print( " - Getting private key for signature of owner %s" % owner)
        privkeys.append(rpc.wallet_dump_private_key(owner)["result"])

    print( "Constructing Deposit operations" )
    wifs = []
    for didx in xrange( 0, args.number ) :
        if args.account :
            address = rpc.wallet_address_create( args.account )[ "result" ]
            wif = rpc.wallet_dump_private_key(address)["result"]
            wifs.append(wif)
        else :
            wif     = Address.newwif()
            address  = Address.wif2btsaddr(wif)
            wifs.append(wif)
        print(" + Address: %s" % address)
        for symbol in fundwith.keys() :
            bIDobj    = have[symbol][1]
            asset     = have[symbol][2]
            asset_id  = asset["id"]
            amount    = fundwith[symbol]
            wst      = Transaction.WithdrawSignatureType( address )
            wc       = Transaction.WithdrawCondition( asset_id, None, "withdraw_signature_type", wst)
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
            spamwriter.writerow([wif, Address.wif2btsaddr(wif), "%s" %sharedroptext, ""])

    # Send operation
    print( json.dumps( sigtx.tojson(), indent=4 ) )
    with open(args.filename,'wb') as fp :
        fp.write(json.dumps(sigtx.tojson()))
    print("Transaction stored in %s" % args.filename)

    if query_yes_no( "Please confirm the transaction" ) :
        print( "Broadcasting transaction to the blockchain" )
        print(rpc.blockchain_broadcast_transaction(sigtx.tojson()))
    else : 
        print("Not broadcasted. Signed transaction stored in file %s" % args.filename)
    rpc.lock()

if __name__ == '__main__':
    main()
