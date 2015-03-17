#!/usr/bin/env python2
import csv
import bitsharestools.address as Address
import bitsharestools.paperwallet as Paper 

design = "cass"

print( "Constructing paper wallets" )
with open('wallet.csv', 'r') as csvfile:
    spamwriter = csv.reader(csvfile, delimiter=';')
    for wif,add,amount,asset in spamwriter :
        ''' Verify that the private keys gives access to address in add '''
        assert Address.priv2btsaddr(Address.wif2hex(wif)) is not add, "private key for address %s is different from given address %s" %(Address.priv2btsaddr(Address.wif2hex(wif)), add) 
        filename = "paperwallets/%s.svg"%add
        print("Creating Paperwallet %s" % (filename))
        svg = Paper.paperwallet(wif, add, amount, asset, design)
        open(filename, 'wb').write(svg)
print( "Done." )
