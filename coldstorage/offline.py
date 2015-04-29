#!/usr/bin/env python2
import json
import sys
import argparse

try :
    import bitsharestools.address as Address
    import bitsharestools.base58 as b58
    import bitsharestools.bip38 as b38
    import bitsharestools.transactions as Transaction
except ImportError :
    raise ImportError('Error importing bitsharestools')

from tools import readtextfromQR, readBalanceFile, ask_for_address, ask_for_decryption, ask_for_privkey, check_availability, input_transfer_asset_balances, addfee, prepare_withdraw

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
        args.address  = ask_for_address() 

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
    with open(args.output,"wb") as fp :
        fp.write(json.dumps(sigtx.tojson()))
    print("\n%d transaction successfully signed and output written to file '%s'" % (len(ops), args.output) )
    print("To broadcast transaction copy the file and run ./online/broadcast_signed_tx.py on online computer")

if __name__ == '__main__':
    main()
