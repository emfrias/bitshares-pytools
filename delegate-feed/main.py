#!/usr/bin/env python3
# coding=utf8 sw=1 expandtab ft=python

import bitsharesrpc
import requests
import json
import sys
from datetime import datetime
import time
from pprint import pprint
import statistics
import re
from math import fabs
import numpy as num
import sys
import config
from prettytable import PrettyTable
import threading

## ----------------------------------------------------------------------------
## When do we have to force publish?
## ----------------------------------------------------------------------------
def publish_rule():
 ##############################################################################
 # - if you haven't published a price in the past 20 minutes
 # - if REAL_PRICE < MEDIAN and YOUR_PRICE > MEDIAN publish price
 # - if REAL_PRICE > MEDIAN and YOUR_PRICE < MEDIAN and abs( YOUR_PRICE - REAL_PRICE ) / REAL_PRICE > 0.005 publish price
 # The goal is to force the price down rapidly and allow it to creep up slowly.
 # By publishing prices more often it helps market makers maintain the peg and
 # minimizes opportunity for shorts to sell USD below the peg that the market
 # makers then have to absorb.
 # If we can get updates flowing smoothly then we can gradually reduce the spread in the market maker bots.
 # *note: all prices in USD per BTS
 # if you haven't published a price in the past 20 minutes, and the price change more than 0.5%
 ##############################################################################
 # YOUR_PRICE = Your current published price.                    = myCurrentFeed[asset]
 # REAL_PRICE = Lowest of external feeds                         = realPrice[asset]
 # MEDIAN = current median price according to the blockchain.    = price_median_blockchain[asset]
 ##############################################################################
 for asset in asset_list_publish :
  ## Define REAL_PRICE
  realPrice[asset] = statistics.median( price["BTS"][asset] )
  ## Rules 
  if (datetime.utcnow()-oldtime[asset]).total_seconds() > config.maxAgeFeedInSeconds :
        print("Feeds for %s too old! Force updating!" % asset)
        return True
  elif realPrice[asset]     < price_median_blockchain[asset] and \
       myCurrentFeed[asset] > price_median_blockchain[asset]:
        print("External price move for %s: realPrice(%.8f) < feedmedian(%.8f) and newprice(%.8f) > feedmedian(%f) Force updating!"\
               % (asset,realPrice[asset],price_median_blockchain[asset],realPrice[asset],price_median_blockchain[asset]))
        return True
  elif fabs(myCurrentFeed[asset]-realPrice[asset])/realPrice[asset] > config.change_min and\
       (datetime.utcnow()-oldtime[asset]).total_seconds() > config.maxAgeFeedInSeconds > 20*60:
        print("New Feeds differs too much for %s %.8f > %.8f! Force updating!" \
               % (asset,fabs(myCurrentFeed[asset]-realPrice[asset]), config.change_min))
        return True
 ## default: False
 return False

## ----------------------------------------------------------------------------
## Fetch data
## ----------------------------------------------------------------------------
def fetch_from_yunbi():
  try :
   url="https://yunbi.com/api/v2/tickers.json"
   response = requests.get(url=url, headers=_request_headers, timeout=3)
   result = response.json()
  except Exception as e:
   print("\nError fetching results from yunbi! ({0})\n".format(str(e)))
   if config.yunbi_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance\n")
   return

  availableAssets = [ "BTS" ]
  for coin in availableAssets :
   if float(result[coin.lower()+"btc"]["ticker"]["last"]) < config.minValidAssetPrice:
    print("\nUnreliable results from yunbi for %s"%(coin))
    continue
   price["BTC"][ coin ].append(float(result[coin.lower()+"btc"]["ticker"]["last"]))
   volume["BTC"][ coin ].append(float(result[coin.lower()+"btc"]["ticker"]["vol"])*config.yunbi_trust_level)

  availableAssets = [ "BTS", "BTC" ]
  for coin in availableAssets :
   if float(result[coin.lower()+"cny"]["ticker"]["last"]) < config.minValidAssetPrice:
    print("Unreliable results from yunbi for %s"%(coin))
    continue
   price["CNY"][ coin ].append(float(result[coin.lower()+"cny"]["ticker"]["last"]))
   volume["CNY"][ coin ].append(float(result[coin.lower()+"cny"]["ticker"]["vol"])*config.yunbi_trust_level)

def fetch_from_btc38():
  url="http://api.btc38.com/v1/ticker.php"
  availableAssets = [ "BTS" ]
  try :
   params = { 'c': 'all', 'mk_type': 'btc' }
   response = requests.get(url=url, params=params, headers=_request_headers, timeout=3 )
   result = response.json()
  except Exception as e:
   print("\nError fetching results from btc38! ({0})\n".format(str(e)))
   if config.btc38_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance!\n")
   return

  for coin in availableAssets :
   if "ticker" in result[coin.lower()] and result[coin.lower()]["ticker"] and float(result[coin.lower()]["ticker"]["last"])>config.minValidAssetPrice:
    price["BTC"][ coin ].append(float(result[coin.lower()]["ticker"]["last"]))
    volume["BTC"][ coin ].append(float(result[coin.lower()]["ticker"]["vol"]*result[coin.lower()]["ticker"]["last"])*config.btc38_trust_level)

  availableAssets = [ "BTS", "BTC" ]
  try :
   params = { 'c': 'all', 'mk_type': 'cny' }
   response = requests.get(url=url, params=params, headers=_request_headers, timeout=3 )
   result = response.json()
  except Exception as e:
   print("\nError fetching results from btc38! ({0})\n".format(str(e)))
   if config.btc38_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance!\n")
   return

  for coin in availableAssets :
   if "ticker" in result[coin.lower()] and result[coin.lower()]["ticker"]  and float(result[coin.lower()]["ticker"]["last"])>config.minValidAssetPrice:
    price["CNY"][ coin ].append(float(result[coin.lower()]["ticker"]["last"]))
    volume["CNY"][ coin ].append(float(result[coin.lower()]["ticker"]["vol"])*float(result[coin.lower()]["ticker"]["last"])*config.btc38_trust_level)

def fetch_from_bter():
  try :
   url="http://data.bter.com/api/1/tickers"
   response = requests.get(url=url, headers=_request_headers, timeout=3 )
   result = response.json()

  except Exception as e:
   print("\nError fetching results from bter! ({0})\n".format(str(e)))
   if config.bter_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance\n")
   return

  availableAssets = [ "BTS" ]
  for coin in availableAssets :
   if float(result[coin.lower()+"_btc"]["last"]) < config.minValidAssetPrice:
    print("Unreliable results from bter for %s"%(coin))
    continue
   price["BTC"][ coin ].append(float(result[coin.lower()+"_btc"]["last"]))
   volume["BTC"][ coin ].append(float(result[coin.lower()+"_btc"]["vol_btc"])*config.bter_trust_level)

  availableAssets = [ "BTC", "BTS" ]
  for coin in availableAssets :
   if float(result[coin.lower()+"_usd"]["last"]) < config.minValidAssetPrice:
    print("Unreliable results from bter for %s"%(coin))
    continue
   price["USD"][ coin ].append(float(result[coin.lower()+"_usd"]["last"]))
   volume["USD"][ coin ].append(float(result[coin.lower()+"_usd"]["vol_usd"])*config.bter_trust_level)

  availableAssets = [ "BTS", "BTC" ]
  for coin in availableAssets :
   if float(result[coin.lower()+"_cny"]["last"]) < config.minValidAssetPrice:
    print("Unreliable results from bter for %s"%(coin))
    continue
   price["CNY"][ coin ].append(float(result[coin.lower()+"_cny"]["last"]))
   volume["CNY"][ coin ].append(float(result[coin.lower()+"_cny"]["vol_cny"])*config.bter_trust_level)

def fetch_from_poloniex():
  try:
   url="https://poloniex.com/public?command=returnTicker"
   response = requests.get(url=url, headers=_request_headers, timeout=3 )
   result = response.json()
   availableAssets = [ "BTS" ]
  except Exception as e:
   print("\nError fetching results from poloniex! ({0})\n".format(str(e)))
   if config.poloniex_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance!\n")
   return
  for coin in availableAssets :
   if float(result["BTC_"+coin]["last"])>config.minValidAssetPrice:
    price["BTC"][ coin ].append(float(result["BTC_"+coin]["last"]))
    volume["BTC"][ coin ].append(float(result["BTC_"+coin]["baseVolume"])*config.poloniex_trust_level)

def fetch_from_bittrex():
  availableAssets = [ "BTSX" ]
  try:
   url="https://bittrex.com/api/v1.1/public/getmarketsummaries"
   response = requests.get(url=url, headers=_request_headers, timeout=3 )
   result = response.json()["result"]
  except Exception as e:
   print("\nError fetching results from bittrex! ({0})\n".format(str(e)))
   if config.bittrex_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance!\n")
   return
  for coin in result :
   if( coin[ "MarketName" ] in ["BTC-"+a for a in availableAssets] ) :
    mObj    = re.match( 'BTC-(.*)', coin[ "MarketName" ] )
    altcoin = mObj.group(1)
    coinmap=altcoin
    if altcoin=="BTSX" : 
     coinmap="BTS"
    if float(coin["Last"]) > config.minValidAssetPrice:
     price["BTC"][ coinmap ].append(float(coin["Last"]))
     volume["BTC"][ coinmap ].append(float(coin["Volume"])*float(coin["Last"])*config.bittrex_trust_level)

def fetch_from_yahoo():
  try :
   for base in _yahoo_base :
    yahooAssets = ",".join([a+base+"=X" for a in _yahoo_quote])
    url="http://download.finance.yahoo.com/d/quotes.csv"
    params = {'s':yahooAssets,'f':'l1','e':'.csv'}
    response = requests.get(url=url, headers=_request_headers, timeout=3 ,params=params)
    yahooprices =  response.text.replace('\r','').split( '\n' )
    for i,a in enumerate(_yahoo_quote) :
     if float(yahooprices[i]) > 0 :
      price[base][ bts_yahoo_map(a) ].append(float(yahooprices[i]))

   # indices
   yahooAssets = ",".join(_yahoo_indices.keys())
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=_request_headers, timeout=3 ,params=params)
   yahooprices =  response.text.replace('\r','').split( '\n' )
   for i,a in enumerate(_yahoo_indices) :
    if float(yahooprices[i]) > 0 :
     price[ list(_yahoo_indices.values())[i] ][ bts_yahoo_map(a) ].append(float(yahooprices[i]))

  except Exception as e:
    sys.exit("\nError fetching results from yahoo! {0}".format(str(e)))

## ----------------------------------------------------------------------------
## Fetch current feeds, assets and feeds of assets from wallet
## ----------------------------------------------------------------------------
def fetch_from_wallet(rpc):
 ## Try to connect to delegate
 rpc.info()
 ## asset definition - mainly for precision
 for asset in asset_list_publish :
  result = rpc.blockchain_get_asset(asset)
  assetprecision[asset] = float(result["result"]["precision"])
  ## feeds for asset
  result = rpc.blockchain_get_feeds_for_asset(asset)
  price_median_blockchain[asset] = 0.0
  for feed in result["result"] :
   if feed["delegate_name"] == "MARKET":
    price_median_blockchain[asset] = float(feed["median_price"])
  time.sleep(.1) # Give time for the wallet to do more important tasks!
 ## feed from delegates
 for delegate in config.delegate_list:
  result = rpc.blockchain_get_feeds_from_delegate(delegate)
  for f in result[ "result" ] :
   myCurrentFeed[ f[ "asset_symbol" ] ] = float(f[ "price" ])
   oldtime[ f[ "asset_symbol" ] ] = datetime.strptime(f["last_update"],"%Y-%m-%dT%H:%M:%S")
  time.sleep(.1) # Give time for the wallet to do more important tasks!

## ----------------------------------------------------------------------------
## Send the new feeds!
## ----------------------------------------------------------------------------
def update_feed(rpc,assets):
 wallet_was_unlocked = False
 
 info = rpc.info()["result"]
 if not info["wallet_open"] :
  print( "Opening wallet %s" % config.wallet )
  ret = rpc.wallet_open(config.wallet)

 if not info["wallet_unlocked"] :
  wallet_was_unlocked = True
  print( "Unlocking wallet" )
  ret = rpc.unlock(999999, config.unlock)

 for delegate in config.delegate_list:
  print("publishing feeds for delegate: %s"%delegate)
  result = rpc.wallet_publish_feeds(delegate, assets)

 if wallet_was_unlocked :
  print( "Relocking wallet" )
  rpc.lock()

## ----------------------------------------------------------------------------
## calculate feed prices in BTS for all assets given the exchange prices in USD,CNY,BTC,...
## ----------------------------------------------------------------------------
def get_btsprice():
 # derive BTS prices for all _base assets
 for base in _bases :
  for quote in _bases :
   if base == quote : continue
   for ratio in price[base][quote] :
    for idx in range(0, len(price[base]["BTS"])) :
     price[quote]["BTS"].append( float("%.8g" % float(price[base]["BTS"][idx] /ratio)))
     volume[quote]["BTS"].append(float("%.8g" % float(volume[base]["BTS"][idx]/ratio)))

 for base in _bases :
  for quote in asset_list_publish :
   for ratio in price[ base ][ quote ] :
    for idx in range(0, len(price[base]["BTS"])) :
     price["BTS"][quote].append( float("%.8g" % float(price[base]["BTS"][idx] /ratio)))
     volume["BTS"][quote].append(float("%.8g" % float(volume[base]["BTS"][idx]/ratio)))

 for asset in asset_list_publish :
  ### Median
  #price_in_bts_average[asset] = statistics.median(price["BTS"][asset])
  ### Mean
  #price_in_bts_average[asset] = statistics.mean(price["BTS"][asset])
  ### Weighted Mean
  assetvolume= [b for b in  volume["BTS"][asset] ]
  assetprice = [a for a in  price["BTS"][asset]  ]
  price_in_bts_weighted[asset] = num.average(assetprice, weights=assetvolume)
  ### Discount
  price_in_bts_weighted[asset] = price_in_bts_weighted[asset] * config.discount

## ----------------------------------------------------------------------------
## Print stats as table
## ----------------------------------------------------------------------------
def print_stats() :
 t = PrettyTable(["asset","BTS/base","my mean","my median","blockchain median","% change (my)","% change (blockchain)","std exchanges","% spread exchanges","last update"])
 t.align                   = 'r'
 t.border                  = True
 t.float_format['BTS/base']              = ".8"
 t.float_format['my mean']               = ".8"
 t.float_format['my median']             = ".8"
 t.float_format['blockchain median']     = ".8"
 t.float_format['% change (my)']         = ".5"
 t.float_format['% change (blockchain)'] = ".5"
 t.float_format['std exchanges']         = ".5"
 t.float_format['% spread exchanges']    = ".5"
 #t.align['BTC']            = "r"
 for asset in asset_list_publish :
    if len(price["BTS"][asset]) < 1 : continue # empty asset
    age                     = (str(datetime.utcnow()-oldtime[asset]))
    weighted_external_price = price_in_bts_weighted[asset]
    prices_from_exchanges   = price["BTS"][asset]
    price_from_blockchain   = price_median_blockchain[asset]
    cur_feed                = myCurrentFeed[asset]
    ## Stats
    mean_exchanges          = 1/statistics.mean(prices_from_exchanges)
    median_exchanges        = 1/statistics.median(prices_from_exchanges)
    spread_exchanges        = 1/((num.max(prices_from_exchanges)-num.min(prices_from_exchanges)) / weighted_external_price*100)
    if cur_feed == 0 :               change_my              = -1
    else :                           change_my              = 1/(((weighted_external_price - float(cur_feed))/float(cur_feed))*100)
    if price_from_blockchain == 0 :  change_blockchain      = -1
    else :                           change_blockchain      = 1/(((weighted_external_price - price_from_blockchain)/price_from_blockchain)*100)
    if len(prices_from_exchanges)<2: std_exchanges          = -1
    else :                           std_exchanges          = 1/(statistics.stdev(prices_from_exchanges)/weighted_external_price*100)
    t.add_row([asset,
               1/weighted_external_price,
               mean_exchanges,
               median_exchanges,
               price_from_blockchain,
               change_my,
               change_blockchain,
               std_exchanges,
               spread_exchanges,
               age ])
 print(t.get_string())

## ----------------------------------------------------------------------------
## Asset rename world<->BTS
## ----------------------------------------------------------------------------
def bts_yahoo_map(asset) :
 if asset in _bts_yahoo_map:
  return _bts_yahoo_map[asset]
 else :
  return asset

## ----------------------------------------------------------------------------
## Run Script
## ----------------------------------------------------------------------------
if __name__ == "__main__":
 _all_bts_assets = ["BTC", "SILVER", "GOLD", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD",
                   "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD",
                   "KRW", "SHENZHEN", "HANGSENG", "NASDAQC", "NIKKEI"]
 _bases =["CNY", "USD", "BTC", "EUR", "HKD", "JPY"]
 _yahoo_base  = ["USD","EUR","CNY","JPY","HKD"]
 _yahoo_quote = ["XAG", "XAU", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD", "KRW"]
 _yahoo_indices = {
                     "399106.SZ" : "CNY",  # SHENZHEN
                     "^HSI"      : "HKD",  # HANGSENG
                     "^IXIC"     : "USD",  # NASDAQC
                     "^N225"     : "JPY"   # NIKKEI
                 }
 _bts_yahoo_map = {
      "XAU"       : "GOLD",
      "XAG"       : "SILVER",
      "399106.SZ" : "SHENZHEN",
      "000001.SS" : "SHANGHAI",
      "^HSI"      : "HANGSENG",
      "^IXIC"     : "NASDAQC",
      "^N225"     : "NIKKEI"
 }
 _request_headers = {'content-type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
 ## Call Parameters ###########################################################
 asset_list_publish = _all_bts_assets
 if len( sys.argv ) > 1 :
  if sys.argv[1] != "ALL":
   asset_list_publish = sys.argv
   asset_list_publish.pop(0)

 ## Initialization
 price_in_bts_weighted   = {}
 myCurrentFeed           = {}
 price_median_blockchain = {}
 realPrice               = {}
 assetprecision          = {}
 assetprecision["BTS"]   = 1e5
 oldtime                 = {}
 price                   = {}
 volume                  = {}

 for base in _bases  + ["BTS"]:
  price[base]            = {}
  volume[base]           = {}
  for asset in _all_bts_assets + ["BTS"]: 
   price[base][asset]    = []
   volume[base][asset]   = []

 for asset in _all_bts_assets + ["BTS"]: 
  price_in_bts_weighted[asset]   = 0.0
  myCurrentFeed[asset]           = 0.0
  price_median_blockchain[asset] = 0.0
  realPrice[asset]               = 0.0
  oldtime[asset]                 = datetime.utcnow()

 ## rpc variables about bts rpc ###############################################
 rpc = bitsharesrpc.client(config.url, config.user, config.passwd)

 ## Get prices and stats ######################################################
 mythreads = {}
 mythreads["wallet"]   = threading.Thread(target = fetch_from_wallet,args = (rpc,))
 mythreads["yahoo"]    = threading.Thread(target = fetch_from_yahoo)
 mythreads["yunbi"]    = threading.Thread(target = fetch_from_yunbi)
 mythreads["btc38"]    = threading.Thread(target = fetch_from_btc38)
 mythreads["bter"]     = threading.Thread(target = fetch_from_bter)
 mythreads["poloniex"] = threading.Thread(target = fetch_from_poloniex)
 mythreads["bittrex"]  = threading.Thread(target = fetch_from_bittrex)

 print("[Starting Threads]: ", end="",flush=True)
 for t in mythreads :
  print("(%s)"%t, end="",flush=True)
  mythreads[t].start()
 for t in mythreads :
  mythreads[t].join() # Will wait for a thread until it finishes its task.

 ## Determine bts price ######################################################
 get_btsprice()

 ## Only publish given feeds ##################################################
 asset_list_final = []
 for asset in asset_list_publish :
  if len(price["BTS"][asset]) > 0 :
   if price_in_bts_weighted[asset] > 0.0:
    asset_list_final.append([ asset, str("%.15f"  % price_in_bts_weighted[asset]) ])

 ## Print some stats ##########################################################
 print_stats()

 ## Check publish rules and publich feeds #####################################
 if publish_rule() :
  print("Update required! Forcing now!")
  update_feed(rpc,asset_list_final)
 else :
  print("no update required")
