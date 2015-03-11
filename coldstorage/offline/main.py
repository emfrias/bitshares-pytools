#!/usr/bin/env python2
import json
import sys

try :
    import bitsharestools.address as Address
    import bitsharestools.base58 as b58
    import bitsharestools.transactions as Transaction
except ImportError :
    raise ImportError('Module bitsharestools missing')

txfee    =  0.5
PREFIX   = "BTS"

'''
1.500000 ; BTS ; 0 ; 100000 ; BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh ; BTS4CNbXqeEym7JopKYvL16qVKUe9kRMMC8x
5.000000 ; EUR ; 21 ; 10000 ; BTSG9SrG1qe2EtDbJkjbTUN4epSNG755P1y7 ; BTS4CNbXqeEym7JopKYvL16qVKUe9kRMMC8x
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

def readtextfromQR():
    try :
        from qrtools import QR
        from codecs import BOM_UTF8
    except ImportError :
        raise ImportError('Module qrtools missing')
    myCode = QR()
    myCode.decode_webcam()
    key = myCode.data_to_string().strip()
    return key[len(BOM_UTF8):] # fixes zbar!

def readonlinedata() :
    print("Please input the results of the online tool and press Enter!: ")
    while True :
        withdrawSet = []
        try :
            lines = iter(raw_input, '')
            for l in lines :
               amount,symbol,assetid,precision,balanceid,owner = l.split(";") 
               withdrawSet.append([ float(amount.strip()), symbol.strip(), int(assetid.strip()), int(precision.strip()), balanceid.strip(), owner.strip()])

            if len( withdrawSet ) :
                break
        except (EOFError, KeyboardInterrupt):
            print # end in newline
            sys.exit(1)
        except :
            print("Error reading input. Try again!")
            continue
    return withdrawSet

def ask_for_target() :
    while True :
        try :
            address = raw_input("Please type the BTS address(!) of the recipient! (wallet_create_address <account>) [empty for QR scanner]: ")
            if address == "" :
                print("Press any key if the green rectangle appears!")
                address = readtextfromQR()
            addressRaw = b58.btsBase58CheckDecode(address[len(PREFIX):])
            return address
        except (EOFError, KeyboardInterrupt):
            print # end in newline
            sys.exit(1)
        except :
            print("Error parsing address. Try again")
            continue

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

if __name__ == '__main__':
    withdrawSet = readonlinedata()

    address  = ask_for_target() 
    privkey  = ask_for_privkey(withdrawSet)

    ops = []
    for w in withdrawSet :
        ops.append(Transaction.Operation("withdraw_op_type", Transaction.Withdraw(w[4], int(w[0]*w[3])) ))

    for w in withdrawSet :
        wst      = Transaction.WithdrawSignatureType( address )
        wc       = Transaction.WithdrawCondition( w[2], None, "withdraw_signature_type", wst)
        deposit  = Transaction.Deposit(int(w[0]*w[3]), wc )
        ops.append(Transaction.Operation( "deposit_op_type", deposit))

    tx       = Transaction.Transaction( 60*60*12, 0, ops )
    sigtx    = Transaction.SignedTransaction(tx, [privkey])

    print( "-"*80 )
    print( "+ output of the offline part (issue this command in the BTS console):" )
    print( "-"*80 )
    print( "\n\n\n\n" )
    print("blockchain_broadcast_transaction " + str(sigtx.tojson()).replace(' ',''))
    print( "\n\n\n\n" )
    print( "-"*80 )
