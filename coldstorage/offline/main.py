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

''' wif: 5Jb8yA5ma656A8WAa6ZvS6cLi7zrw2XN1paoR3CAckda5BytiiQ '''

'''
1.500000 ; BTS ; 0 ; 100000 ; BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh ; BTSDSBrr8hCzoEEWrm6GhjzesewFcXVmR88j
5.000000 ; EUR ; 21 ; 10000 ; BTSG9SrG1qe2EtDbJkjbTUN4epSNG755P1y7 ; BTSDSBrr8hCzoEEWrm6GhjzesewFcXVmR88j
'''

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
Meta function to read stuff from QR code
'''
def readtextfromQR():
    try :
        from qrtools import QR
        from codecs import BOM_UTF8
    except ImportError :
        print('Module qrtools missing! No QR-code import possible!')
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
        print("Available funds in the cold storage address:")
        for l in fp.readlines() :
            try :
                amount,symbol,assetid,precision,balanceid,owner = l.split(";") 
                balances.append([ float(amount.strip()), symbol.strip(), int(assetid.strip()), int(precision.strip()), balanceid.strip(), owner.strip()])
                print( " - %f %s" %( float(amount.strip()), symbol.strip() ) )
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
            print("Error parsing address. Try again!")
            continue

'''
Ask for the private key, if not manual (copy/pase) then go to QR-codes
'''
def ask_for_privkey(address) :
    while True :
        try :
            print("Require private key for address %s. How would you like to provide the private key?" % (address) )
            print("1) Type in WIF private key")
            print("2) Use QR scanner")
            choice = raw_input("Select option: ")
            if choice == "1" :
                privkey = raw_input("Please provide private key (WIF): ")
            elif choise == "2" :
                print("Press any key if the green rectangle appears!")
                privkey = readtextfromQR()
            else :
                continue
            ''' Verify that the given private key gives access to the cold storage address '''
            addressraw = Address.priv2btsaddr(Address.wif2hex(privkey))
            print("This private key gives access to funds in address %s" % addressraw)
            if str(address).strip() == str(addressraw).strip() :
                return str(privkey).strip()
            else :
                print("The private key is wrong! It gives access to %s but access to %s is required to sign this tx" % (addressraw, address))
                raise
        except (EOFError, KeyboardInterrupt):
            print
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
                raise Exception("You don't have %f %s" %( want[b], b ))
            continue
        else :
            raise Exception("You dont have a balance %d" % b)

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
                amount     = want[w]
                symbol     = h[1]
                asset_id   = h[2]
                precision  = h[3]
                balance_id = h[4]
                owner      = h[5]
                s.append( [ amount*precision, symbol, asset_id, precision, balance_id, owner ] )
    return s

def main() :
    global PREFIX
    parser = argparse.ArgumentParser(description='Online tool to define and sign transaction from coldstorage')
    parser.add_argument('--address', type=str, help='Address to send the funds to (hot address) (default: scan per QR-code)')
    parser.add_argument('--filename', type=str, help='File created by the online tool containing available balances')
    parser.add_argument('--txfee', type=float, help='txfee substracted from your funds')
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

    ''' Read the balance file '''
    availableBalance     = readBalanceFile(args.filename)

    ''' Ask the user to input the funds to be transfered '''
    transferbalances     = input_transfer_asset_balances()

    ''' Add the TX fee in BTS '''
    transferbalances     = addfee(transferbalances, args.txfee)

    ''' Check if the funds entered (plus fee) can be paid '''
    check_availability(availableBalance, transferbalances)

    ''' construct withdrawal amounts and assets '''
    withdrawSet = prepare_withdraw( availableBalance, transferbalances )

    ''' Ask for the target address if not given as parameter '''
    if not args.address :
        args.address  = ask_for_target() 

    ''' Construct the transaction '''
    ops = []
    for w in withdrawSet :
        amount    = w[0]
        asset_id  = w[2]
        balanceid = w[4]

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

    print("Raw and unsigned transaction for verification:")
    print(json.dumps( tx.tojson(  ), indent=4 ) )

    print("The following funds will be moved out of cold storage:")
    for w in withdrawSet :
        amount    = w[0]
        symbol    = w[1]
        precision = w[3]
        print(" - %f %s" %(amount/precision, symbol))
    print("%d Operation(s) need to be signed." % (len(ops)) )

    ''' Ask for the private key '''
    privkey  = ask_for_privkey(withdrawSet[0][5])

    ''' Sign transaction '''
    sigtx    = Transaction.SignedTransaction(tx, [privkey])

    ''' Store signed transaction '''
    with open(args.output,"w") as fp :
        fp.write(str(sigtx.tojson()).replace(' ',''))
    print("\n%d transaction successfully signed and output written to file '%s'" % (len(ops), args.output) )
    print("To broadcast transaction run ./broadcast/main.py '%s' on online computer" % args.output)

if __name__ == '__main__':
    main()
