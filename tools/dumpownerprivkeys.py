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
    print " # Owner keys "
    print "---------------------------------------------------------------------------------"
    for account in accounts :
        try : 
            print "wallet_import_private_key %s   # %20s" % (rpc.wallet_dump_account_private_key(account["name"], "owner_key")["result"], account["name"])
        except :
            print "%20s - owner key unknown" % (account["name"])

    print "---------------------------------------------------------------------------------"
    print rpc.lock()
