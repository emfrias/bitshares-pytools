#!/usr/bin/python

import bitsharesrpc
import config
  
if __name__ == "__main__" :
    rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
    rpc.wallet_open(config.wallet)
    rpc.unlock(9999,config.unlock)
    r = (rpc.wallet_list_accounts())
    accounts = r["result"]
    print "---------------------------------------------------------------------------------"
    print " # Currently active keys"
    print "---------------------------------------------------------------------------------"
    for account in accounts :
        try : 
            print "wallet_import_private_key %s   # %20s" % (rpc.wallet_dump_account_private_key(account["name"], "active_key")["result"], account["name"])
        except :
            print "%20s - active key unknown" % (account["name"])

    print "---------------------------------------------------------------------------------"
    print " # Active key history"
    print "---------------------------------------------------------------------------------"
    for account in accounts :
        for a in account["active_key_history"] :
            address = a[1]
            if address is account["owner_key"] : continue ## make sure not to dump the owner key
            try : 
                wif = rpc.wallet_dump_private_key(address)["result"]
                if wif is not None :
                    print "wallet_import_private_key %s   # %20s" % (wif, account["name"])
            except : pass

    print "---------------------------------------------------------------------------------"
    print rpc.lock()
