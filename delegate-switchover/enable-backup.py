#!/usr/bin/python
import csv
import os
import bitsharesrpc
import config

rpc2  = bitsharesrpc.client(config.backupurl, config.backupuser, config.backuppasswd)
rpc  = bitsharesrpc.client(config.mainurl, config.mainuser, config.mainpasswd)

def enable( ) :
    print "checking connectivity"
    rpc2.info()
#    rpc.info()

    print "enabling backup block production"
    rpc2.wallet_open("delegate")
    rpc2.wallet_delegate_set_block_production("ALL","true")
    rpc2.unlock(9999999, config.backupunlock)
    #rpc2.setnetwork(25,30)

    print "disabling main block production"
    rpc.wallet_open("delegate")
    rpc.lock()
    rpc.wallet_delegate_set_block_production("ALL","false")

if __name__ == "__main__":
 enable(  )
