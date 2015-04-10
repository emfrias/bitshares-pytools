#!/usr/bin/python

import bitsharesrpc
import config
  
if __name__ == "__main__" :
    rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
    rpc.wallet_open(config.wallet)
    rpc.unlock(9999,config.unlock)
    r = (rpc.wallet_list_my_accounts())
    accounts = r["result"]
    print "---------------------------------------------------------------------------------"
    print " # Currently signing keys"
    print "---------------------------------------------------------------------------------"
    for account in accounts :
        if "delegate_info" in account :
            try : 
                print "wallet_import_private_key %s   # %20s" % (rpc.wallet_dump_account_private_key(account["name"], "signing_key")["result"], account["name"])
            except :
                print "%20s - signing key unknown" % (account["name"])

    print "---------------------------------------------------------------------------------"
    print " # signing key history"
    print "---------------------------------------------------------------------------------"
    for account in accounts :
        if "delegate_info" in account and account["delegate_info"]:
            for a in account["delegate_info"]["signing_key_history"] :
                address = a[1]
                wif = rpc.wallet_dump_private_key(address)["result"]
                if wif is not None :
                    print "wallet_import_private_key %s   # %20s" % (wif, account["name"])

    print "---------------------------------------------------------------------------------"
    rpc.lock()
