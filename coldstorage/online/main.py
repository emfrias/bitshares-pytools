#!/usr/bin/env python2
import sys
import config
import bitsharesrpc

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

def input_transfer_asset_balances() :
    withdraw = {}
    while True :
        i = raw_input("Give amount AND asset [10 BTS]: ")
        try :
            amount,assetname = i.split(" ")
            asset  = rpc.blockchain_get_asset(assetname)["result"]
            amount = float(amount)
            withdraw[ asset["symbol"] ] = float(amount)
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

def addfee( w ) :
    print("Adding tx fee of %f BTS" % config.txfee)
    if "BTS" in w.keys() :
        w["BTS"] += float(config.txfee)
    else :
        w["BTS"] = float(config.txfee)
    return w

def get_available_balances():
    availableBalance = {}
    balanceIDs       = {}
    precisions       = {}
    assetIDs         = {}
    ownerIDs         = {}
    balances = rpc.blockchain_list_address_balances(config.coldaddress)["result"]
    print("Available balances:")
    for b in balances :
        balanceId = b[0]
        asset_id  = b[1]["condition"]["asset_id"]
        owner     = b[1]["condition"]["data"]["owner"]
        asset     = rpc.blockchain_get_asset(asset_id)["result"]
        balance   = b[1]["balance"]/float(asset["precision"])
        print("%f %s" %(balance, asset["symbol"]))
        availableBalance[ asset[ "symbol" ] ] = balance
        balanceIDs[ asset[ "symbol" ] ]       = balanceId
        precisions[ asset[ "symbol" ] ]       = asset[ "precision" ]
        assetIDs[ asset[ "symbol" ] ]         = asset[ "id" ]
        ownerIDs[ asset[ "symbol" ] ]         = owner
    return availableBalance, balanceIDs, assetIDs, precisions, ownerIDs

def check_availability(have, want) :
    availableAssets = []
    for b in want.keys() : 
        if b in have.keys() :
            if want[b] > have[b] : 
                raise Exception("You don't have %f in asset %s" %( want[b], b ))
            continue
        else :
            raise Exception("You dont have a balance in asset %d" % b)

if __name__ == '__main__':
    print( "Connecting to BitShares RPC" )
    rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
    rpc.wallet_open(config.wallet)
    rpc.unlock(999999, config.unlock)

    balances,balanceids,assetids,precisions,owners  = get_available_balances()
    transferbalances     = input_transfer_asset_balances()
    transferbalances     = addfee(transferbalances)
    check_availability(balances, transferbalances)

    print( "-"*80 )
    print( "+ input for the offline part:" )
    print( "-"*80 )
    print( "\n\n\n\n" )
    for t in transferbalances.keys() :
        print( "%f ; %s ; %d ; %d ; %s ; %s" %(transferbalances[t], t, assetids[t], precisions[t], balanceids[t], owners[t]) )
    print( "\n\n\n\n" )
    print( "-"*80 )
