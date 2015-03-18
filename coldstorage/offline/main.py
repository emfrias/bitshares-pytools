#!/usr/bin/env python2
import json
import sys
import argparse

try :
    import bitsharestools.address as Address
    import bitsharestools.base58 as b58
    import bitsharestools.transactions as Transaction
except ImportError :
    raise ImportError('Module bitsharestools missing')

'''
1.500000 ; BTS ; 0 ; 100000 ; BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh ; BTS4CNbXqeEym7JopKYvL16qVKUe9kRMMC8x
5.000000 ; EUR ; 21 ; 10000 ; BTSG9SrG1qe2EtDbJkjbTUN4epSNG755P1y7 ; BTS4CNbXqeEym7JopKYvL16qVKUe9kRMMC8x
'''


'''
Meta function to read stuff from QR code
'''
def readtextfromQR():
    try :
        from qrtools import QR
        from codecs import BOM_UTF8
    except ImportError :
        print('Module qrtools missing')
        raise 
    myCode = QR()
    myCode.decode_webcam()
    key = myCode.data_to_string().strip()
    return key[len(BOM_UTF8):] # fixes zbar!

'''
Read the balance file given from the online tool and return the available data
'''
def readBalanceFile(filename) :
    balances = [  ]
    with open( filename, "rb" ) as fp :
        print("Available funds:")
        for l in fp.readlines() :
            try :
                amount,symbol,assetid,precision,balanceid,owner = l.split(";") 
                balances.append([ float(amount.strip()), symbol.strip(), int(assetid.strip()), int(precision.strip()), balanceid.strip(), owner.strip()])
                print( "%f %s" %( float(amount.strip()), symbol.strip() ) )
            except :
                print("Syntax error in file. Try again!")
                raise
    return balances

'''
If not given as parameter, ask the user for the hot wallet address
'''
def ask_for_target() :
    global PREFIX
    while True :
        try :
            address = raw_input("Please type the BTS address(!) of the recipient! (wallet_create_address <account>) [empty for QR scanner]: ")
            if address == "" :
                print("Press any key if the green rectangle appears!")
                address = readtextfromQR()
            b58.btsBase58CheckDecode(address[len(PREFIX):])
            return address
        except (EOFError, KeyboardInterrupt):
            print # end in newline
            sys.exit(1)
        except :
            print("Error parsing address. Try again")
            continue

'''
Ask for the private key, if not manual (copy/pase) then go to QR-codes
'''
def ask_for_privkey(withdraw) :
    while True :
        try :
            privkey = raw_input("Please type private key [empty for QR scanner]: ")
            if privkey == "" :
                print("Press any key if the green rectangle appears!")
                privkey = readtextfromQR()
            address = Address.priv2btsaddr(Address.wif2hex(privkey))
            print("This private key gives access to funds in address %s" % address)
            for w in withdraw :
                if address is not w[5] :
                    print("The private key is wrong! It gives access to %s but access to %s is required to sign this tx" % (address, w[5]))
                    raise
            return privkey
        except (EOFError, KeyboardInterrupt):
            print # end in newline
            sys.exit(1)
        except :
            print("Error parsing privkey. Try again")
            continue

'''
Verify that the funds the user wants to withdraw are available according to the balance file
'''
def check_availability(balances, want) :
    have = {}
    for b in balances :
        have[ b[1] ] = b[0]
    for b in want.keys() : 
        if b in have.keys() :
            if want[b] > have[b] : 
                raise Exception("You don't have %f in asset %s" %( want[b], b ))
            continue
        else :
            raise Exception("You dont have a balance in asset %d" % b)

'''
Meta function to have yes/no questions
'''
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

'''
Ask user to input the amount of funds he wants to withdraw
'''
def input_transfer_asset_balances() :
    withdraw = {}
    while True :
        i = raw_input("Give amount AND asset [10 BTS]: ")
        try :
            amount,assetname = i.split(" ")
            withdraw[ assetname ] = float(amount)
        except :
            print("Error reading input. Try again! Example: 10 BTS")
            continue

        print("Going to withdraw:")
        for w in withdraw.keys() :
            print("%f %s" %( withdraw[w], w))

        if query_yes_no( "Want more?" ) :
            continue
        break
    withdrawUnique = {}
    for b in withdraw.keys() :
        if b in withdrawUnique.keys() :
            withdrawUnique[ b ] += withdraw[b]
        else :
            withdrawUnique[ b ] = withdraw[b]
    return withdrawUnique

'''
Add the txfee as BTS
'''

def addfee( w, fee ) :
    fee = float( fee )
    print("Adding tx fee of %f BTS" % fee)
    if "BTS" in w.keys() :
        w["BTS"] += fee
    else :
        w["BTS"] = fee
    return w

''' 
Prepare an array of data used to construct the transaction
'''
def prepare_withdraw( have, want ) :
    s = []
    for w in want.keys() : 
        for h in have :
            if w in h :
                precision = h[3]
                amount = want[w]
                asset_id = h[2]
                balance_id = h[4]
                s.append( [ amount*precision, asset_id, balance_id ] )
    return s

def main() :
    parser = argparse.ArgumentParser(description='Online tool to define and sign transaction from coldstorage')
    parser.add_argument('--filename', type=str, help='File created by the online tool containing available balances')
    parser.add_argument('--txfee', type=float, help='txfee substracted from your funds')
    parser.add_argument('--address', type=str, help='Address to send the funds to (hot address) (default: scan per QR-code)')
    parser.add_argument('--prefix', type=str, help='defaults to "BTS" (advanced feature)')
    parser.add_argument('--output', type=str, help='filename into which the signed output is stored')
    parser.set_defaults(filename="availablefunds.txt", output="signedtx.txt", txfee=0.5)
    parser.set_defaults(prefix="BTS")
    args = parser.parse_args()
    PREFIX   = args.prefix

    ''' If an address is given, verify validity '''
    if args.address :
        try :
            b58.btsBase58CheckDecode(args.address[len(PREFIX):])
        except :
            raise Exception("Invalid address format")

    availableBalance     = readBalanceFile(args.filename)
    transferbalances     = input_transfer_asset_balances()
    transferbalances     = addfee(transferbalances, args.txfee)
    check_availability(availableBalance, transferbalances)
    withdrawSet = prepare_withdraw( availableBalance, transferbalances )

    if not args.address :
        args.address  = ask_for_target() 
    privkey  = ask_for_privkey(availableBalance)

    ops = []
    for w in withdrawSet :
        amount    = w[0]
        asset_id  = w[1]
        balanceid = w[2]

        ''' Withdrawal from coldstorage '''
        ops.append(Transaction.Operation("withdraw_op_type", Transaction.Withdraw(balanceid, int(amount)) ))

        ''' Deposit to hot wallet '''
        if asset_id == 0 : # substract txfee
            amount -= args.txfee * 1e5
            if not amount :
                continue
        wst      = Transaction.WithdrawSignatureType( args.address )
        wc       = Transaction.WithdrawCondition( asset_id, None, "withdraw_signature_type", wst)
        deposit  = Transaction.Deposit(int(amount), wc )
        ops.append(Transaction.Operation( "deposit_op_type", deposit))

    tx       = Transaction.Transaction( 60*60*12, 0, ops )
    sigtx    = Transaction.SignedTransaction(tx, [privkey])

    print( "-"*80 )
    print( "+ Raw and signed transaction for verification:" )
    print( "-"*80 )
    print( json.dumps( sigtx.tojson(  ), indent=4 ) )
    print( "-"*80 )
    print( "+ stripped output of signed transaction (issue this command in the BTS console):" )
    print( "-"*80 )
    print( "\n\n\n\n" )
    print("blockchain_broadcast_transaction " + str(sigtx.tojson()).replace(' ',''))
    print( "\n\n\n\n" )
    print( "-"*80 )
    with open(args.output,"w") as fp :
        fp.write(str(sigtx.tojson()).replace(' ',''))
    print( "+ signed transaction stored in file %s" % args.output )
    print( "-"*80 )

if __name__ == '__main__':
    main()
