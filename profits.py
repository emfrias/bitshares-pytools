#!/usr/bin/env python3
# coding=utf8 sw=1 expandtab ft=python

import sys
from datetime import datetime
import time
from btsx import BTSX
from config import read_config
from bots import MarketMaker
from bots import MarketSpeculator
from bots import MarketBalance
import exchanges as ex
from pprint import pprint
import re

## Loading Config
config = read_config(sys.argv[1])

## Opening RPC to wallet
client = BTSX(
    config["client"]["rpc_user"],
    config["client"]["rpc_password"],
    config["client"]["rpc_host"],
    config["client"]["rpc_port"]
)

for botconfig in config["bots"] :
    name           = botconfig["account_name"]
    quote          = botconfig["asset_pair"][0]
    base           = botconfig["asset_pair"][1]
    baseid         = client.get_asset_id(base)
    quoteid        = client.get_asset_id(quote)
    basePrecision  = client.get_precision(base)
    quotePrecision = client.get_precision(quote)
    print("#"*100)
    print("#"*100)
    print("Bot: %s - Market: %s/%s" % (name, quote, base))
    print("#"*100)
    print("#"*100)
    print("")

    ## Get transactions that fund the bot #####################################
    funding = {}
    funding[ baseid  ] = 0
    funding[ quoteid ] = 0
    trades = client.get_tx_history(name, "")
    for i in sorted(trades, key=lambda item:item["block_num"]) :
        is_cancel            = i["is_market_cancel"]
        blocknum             = i["block_num"]
        is_market            = i["is_market"]
        if is_cancel : continue
        if is_market : continue 
        for l in i["ledger_entries"] :
            if( l[ "memo" ] == "yield" ) : continue ## skip yields
            asset_id            = l["amount"]["asset_id"]
            precision           = basePrecision if asset_id == baseid else quotePrecision
            amount              = l["amount"]["amount"] / precision
            matchObjA = re.match( r'^(ASK)|(BID)', l["from_account"], re.M|re.I)
            matchObjB = re.match( r'^(ASK)|(BID)', l["to_account"], re.M|re.I)
            if matchObjA or matchObjB: continue # skip market
            if l["to_account"] == name : funding[ asset_id ] += amount
            else :                       funding[ asset_id ] -= amount

    ## Get Balances ###########################################################
    last_price   = client.get_last_fill(quote, base) * (basePrecision / quotePrecision)
    balanceBase  = client.get_balance(name, base)
    balanceQuote = client.get_balance(name, quote)

    ## Adjust by open orders ##################################################
    open_orders  = client.get_all_orders(name, quote, base)
    for o in open_orders[ 1 ] :
       if   o[ "type" ] == "ask_order" : balanceBase  += float(o["state"]["balance"]) / basePrecision  # balance in base
       elif o[ "type" ] == "bid_order" : balanceQuote += float(o["state"]["balance"]) / quotePrecision # balance in quote
       else : raise Exception( "This bot only runs with a separate account name!" )

    ## Output #################################################################
    print('+'*65)
    print('Balance: %20.8f %4s = %20.8f %4s' %(balanceBase, base, balanceBase*last_price, quote))
    print('Balance: %20.8f %4s = %20.8f %4s' %(balanceQuote, quote, balanceQuote/last_price, base))
    print('-'*65)
    print('Sum:     %20.8f %4s = %20.8f %4s' %(balanceBase+balanceQuote/last_price, base, balanceBase*last_price+balanceQuote, quote))
    print('+'*65)
    print('Funding: %20.8f %4s = %20.8f %4s' %(funding[baseid],  base,  funding[baseid]*last_price,  quote))
    print('Funding: %20.8f %4s = %20.8f %4s' %(funding[quoteid], quote, funding[quoteid]/last_price, base))
    print('-'*65)
    diffBase  = balanceBase-funding[baseid]
    diffQuote = balanceQuote-funding[quoteid]
    print('Profits: %20.8f %4s = %20.8f %4s' %( diffBase + diffQuote/last_price, base,\
                                                diffBase*last_price+(diffQuote), quote) )
    print('+'*65)

    ## List individual trades #################################################
    event          = []
    fee            = {}
    fee[baseid]    = 0
    fee[quoteid]   = 0
    for i in sorted(trades, key=lambda item:item["block_num"]) :
        is_cancel            = i["is_market_cancel"]
        blocknum             = i["block_num"]
        is_market            = i["is_market"]
        if is_cancel     : continue
        if not is_market : continue
        fee_asset            = i["fee"]["asset_id"]
        fee[fee_asset]      += i["fee"]["amount"] / client.get_precision( fee_asset )
        for l in i["ledger_entries"] :
            if re.match( r'^(ASK)|(BID)|(yield)', l["memo"], re.M|re.I) : continue ## not show orders -- just filled orders
            asset_id            = l["amount"]["asset_id"]
            precision           = basePrecision if asset_id == baseid else quotePrecision
            amount              = l["amount"]["amount"] / precision
            runningBalanceAsset = l[ "running_balances" ][ 0 ][ 1 ][ 0 ][ 1 ][ "asset_id" ]
            precision           = basePrecision if runningBalanceAsset == baseid else quotePrecision
            runningBalance      = l[ "running_balances" ][ 0 ][ 1 ][ 0 ][ 1 ][ "amount" ] / precision
            price               = 0
            matchObj = re.match( r'.*@ ([\d\.]* )', l["memo"], re.M|re.I) # order price?
            if ( matchObj ): price = matchObj.group(1)
            eventit = {'height' : blocknum,
                       'amount' : float(amount),
                       'assetid': asset_id,
                       'from'   : l["from_account"],
                       'to'     : l["to_account"],
                       'ismarket':is_market,
                       'price'  : float(price),
                       'memo'   : l["memo"]
                      }
            event.append(eventit)
    print( "Orders "+"="*(120-12) )
    for o in sorted(event, key  = lambda item:item["height"]) :
        print( "Height: %8d  Amount: %14.8f %4s  Price: %14.8f --- %50s" %(o["height"], o["amount"], quote if o["assetid"]==quoteid else base, o["price"], o["memo"]) )
    print('\n\n')
