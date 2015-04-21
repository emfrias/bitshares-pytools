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
  realPrice[asset] = statistics.median( price_in_bts[asset] )
  ## Rules 
  if (datetime.utcnow()-oldtime[asset]).total_seconds() > config.maxAgeFeedInSeconds :
        print("Feeds for %s too old! Force updating!" % asset)
        return True
  elif realPrice[asset]     < price_median_blockchain[asset] and \
       myCurrentFeed[asset] > price_median_blockchain[asset]:
        print("External price move for %s: realPrice(%f) < feedmedian(%f) and newprice(%f) > feedmedian(%f) Force updating!"\
               % (asset,realPrice[asset],price_median_blockchain[asset],realPrice[asset],price_median_blockchain[asset]))
        return True
  elif fabs(myCurrentFeed[asset]-realPrice[asset])/realPrice[asset] > config.change_min and\
       (datetime.utcnow()-oldtime[asset]).total_seconds() > config.maxAgeFeedInSeconds > 20*60:
        print("New Feeds differs too much for %s %.2f > %.2f! Force updating!" \
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
   response = requests.get(url=url, headers=headers, timeout=3)
   result = response.json()
  except:
   print("Error fetching results from yunbi!")
   if config.yunbi_trust_level > 0.8:
    sys.exit("Exiting due to exchange importance")
   return

  availableAssets = [ "BTS" ]
  for coin in availableAssets :
   if float(result[coin.lower()+"btc"]["ticker"]["last"]) < config.minValidAssetPrice:
    print("Unreliable results from yunbi for %s"%(coin))
    continue
   price_in_btc[ coin ].append(float(result[coin.lower()+"btc"]["ticker"]["last"]))
   volume_in_btc[ coin ].append(float(result[coin.lower()+"btc"]["ticker"]["vol"])*config.yunbi_trust_level)

  availableAssets = [ "BTS", "BTC" ]
  for coin in availableAssets :
   if float(result[coin.lower()+"cny"]["ticker"]["last"]) < config.minValidAssetPrice:
    print("Unreliable results from yunbi for %s"%(coin))
    continue
   price_in_cny[ coin ].append(float(result[coin.lower()+"cny"]["ticker"]["last"]))
   volume_in_cny[ coin ].append(float(result[coin.lower()+"cny"]["ticker"]["vol"])*config.yunbi_trust_level)

def fetch_from_btc38():
  url="http://api.btc38.com/v1/ticker.php"
  availableAssets = [ "BTS" ]
  try :
   params = { 'c': 'all', 'mk_type': 'btc' }
   response = requests.get(url=url, params=params, headers=headers, timeout=3 )
   result = response.json()
  except: 
   print("Error fetching results from btc38!")
   if config.btc38_trust_level > 0.8:
    sys.exit("Exiting due to exchange importance!")
   return

  for coin in availableAssets :
   if "ticker" in result[coin.lower()] and result[coin.lower()]["ticker"] and float(result[coin.lower()]["ticker"]["last"])>config.minValidAssetPrice:
    price_in_btc[ coin ].append(float(result[coin.lower()]["ticker"]["last"]))
    volume_in_btc[ coin ].append(float(result[coin.lower()]["ticker"]["vol"]*result[coin.lower()]["ticker"]["last"])*config.btc38_trust_level)

  availableAssets = [ "BTS", "BTC" ]
  try :
   params = { 'c': 'all', 'mk_type': 'cny' }
   response = requests.get(url=url, params=params, headers=headers, timeout=3 )
   result = response.json()
  except: 
   print("Error fetching results from btc38!")
   if config.btc38_trust_level > 0.8:
    sys.exit("Exiting due to exchange importance!")
   return

  for coin in availableAssets :
   if "ticker" in result[coin.lower()] and result[coin.lower()]["ticker"]  and float(result[coin.lower()]["ticker"]["last"])>config.minValidAssetPrice:
    price_in_cny[ coin ].append(float(result[coin.lower()]["ticker"]["last"]))
    volume_in_cny[ coin ].append(float(result[coin.lower()]["ticker"]["vol"])*float(result[coin.lower()]["ticker"]["last"])*config.btc38_trust_level)

def fetch_from_bter():
  try :
   url="http://data.bter.com/api/1/tickers"
   response = requests.get(url=url, headers=headers, timeout=3 )
   result = response.json()

  except:
   print("Error fetching results from bter!")
   if config.bter_trust_level > 0.8:
    sys.exit("Exiting due to exchange importance")
   return

  availableAssets = [ "BTS" ]
  for coin in availableAssets :
   if float(result[coin.lower()+"_btc"]["last"]) < config.minValidAssetPrice:
    print("Unreliable results from bter for %s"%(coin))
    continue
   price_in_btc[ coin ].append(float(result[coin.lower()+"_btc"]["last"]))
   volume_in_btc[ coin ].append(float(result[coin.lower()+"_btc"]["vol_btc"])*config.bter_trust_level)

  availableAssets = [ "BTC", "BTS" ]
  for coin in availableAssets :
   if float(result[coin.lower()+"_usd"]["last"]) < config.minValidAssetPrice:
    print("Unreliable results from bter for %s"%(coin))
    continue
   price_in_usd[ coin ].append(float(result[coin.lower()+"_usd"]["last"]))
   volume_in_usd[ coin ].append(float(result[coin.lower()+"_usd"]["vol_usd"])*config.bter_trust_level)

  availableAssets = [ "BTS", "BTC" ]
  for coin in availableAssets :
   if float(result[coin.lower()+"_cny"]["last"]) < config.minValidAssetPrice:
    print("Unreliable results from bter for %s"%(coin))
    continue
   price_in_cny[ coin ].append(float(result[coin.lower()+"_cny"]["last"]))
   volume_in_cny[ coin ].append(float(result[coin.lower()+"_cny"]["vol_cny"])*config.bter_trust_level)

def fetch_from_poloniex():
  try:
   url="https://poloniex.com/public?command=returnTicker"
   response = requests.get(url=url, headers=headers, timeout=3 )
   result = response.json()
   availableAssets = [ "BTS" ]
  except:
   print("Error fetching results from poloniex!")
   if config.poloniex_trust_level > 0.8:
    sys.exit("Exiting due to exchange importance!")
   return
  for coin in availableAssets :
   if float(result["BTC_"+coin.upper()]["last"])>config.minValidAssetPrice:
    price_in_btc[ coin ].append(float(result["BTC_"+coin.upper()]["last"]))
    volume_in_btc[ coin ].append(float(result["BTC_"+coin.upper()]["baseVolume"])*config.poloniex_trust_level)

def fetch_from_bittrex():
  availableAssets = [ "BTSX" ]
  try:
   url="https://bittrex.com/api/v1.1/public/getmarketsummaries"
   response = requests.get(url=url, headers=headers, timeout=3 )
   result = response.json()["result"]
  except:
   print("Error fetching results from bittrex!")
   if config.bittrex_trust_level > 0.8:
    sys.exit("Exiting due to exchange importance!")
   return
  for coin in result :
   if( coin[ "MarketName" ] in ["BTC-"+a for a in availableAssets] ) :
    mObj    = re.match( 'BTC-(.*)', coin[ "MarketName" ] )
    altcoin = mObj.group(1)
    coinmap=altcoin
    if altcoin=="BTSX" : 
     coinmap="BTS"
    if float(coin["Last"]) > config.minValidAssetPrice:
     price_in_btc[ coinmap ].append(float(coin["Last"]))
     volume_in_btc[ coinmap ].append(float(coin["Volume"])*float(coin["Last"])*config.bittrex_trust_level)

def fetch_from_yahoo():
#  try :
   availableAssets = ["XAG", "XAU", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD", "KRW"]
   ## USD/X
   yahooAssets = ",".join(["USD"+a+"=X" for a in availableAssets])
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers, timeout=3 ,params=params)
   yahooprices =  response.text.replace('\r','').split( '\n' )
   for i,a in enumerate(availableAssets,1) :
    price_in_usd[ bitassetname(a.upper()) ].append(1/float(yahooprices[i-1])) # flipped market
   ## CNY/X
   yahooAssets = ",".join([a+"CNY=X" for a in availableAssets])
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers, timeout=3 ,params=params)
   yahooprices =  response.text.replace('\r','').split( '\n' )
   for i,a in enumerate(availableAssets,1) :
    price_in_cny[ bitassetname(a.upper()) ].append(float(yahooprices[i-1])) ## market is the other way round! (yahooAssets)
   ## EUR/X
   yahooAssets = ",".join(["EUR"+a+"=X" for a in availableAssets])
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers, timeout=3 ,params=params)
   yahooprices =  response.text.replace('\r','').split( '\n' )
   for i,a in enumerate(availableAssets,1) :
    price_in_eur[ bitassetname(a.upper()) ].append(float(yahooprices[i-1]))
#  except:
#   sys.exit("Warning: unknown error - yahoo")

## ----------------------------------------------------------------------------
## GOLD=XAU  SILVER=XAG
## ----------------------------------------------------------------------------
def bitassetname(asset) :
 if asset == "XAU" : 
  return "GOLD"
 elif asset == "XAG" : 
  return "SILVER"
 else :
  return asset

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
 for delegate in delegate_list:
  result = rpc.blockchain_get_feeds_from_delegate(delegate)
  for f in result[ "result" ] :
   myCurrentFeed[ f[ "asset_symbol" ] ] = float(f[ "price" ])
   oldtime[ f[ "asset_symbol" ] ] = datetime.strptime(f["last_update"],"%Y-%m-%dT%H:%M:%S")
  time.sleep(.1) # Give time for the wallet to do more important tasks!

## ----------------------------------------------------------------------------
## Send the new feeds!
## ----------------------------------------------------------------------------
def update_feed(rpc,assets):
 ## Try to connect to delegate
 rpc.info()
 ## unlock wallet
 print( "Opening wallet %s" % config.wallet )
 ret = rpc.wallet_open(config.wallet)
 print( "Unlocking wallet" )
 ret = rpc.unlock(999999, config.unlock)
 # for each delegate update the list
 for delegate in delegate_list:
  print("publishing feeds for delegate: %s"%delegate)
  result = rpc.wallet_publish_feeds(delegate, assets)
 ## close wallet
 rpc.lock()

## ----------------------------------------------------------------------------
## calculate feed prices in BTS for all assets given the exchange prices in USD,CNY,BTC
## ----------------------------------------------------------------------------
def get_btsprice():
 for asset in asset_list_publish :
  price_in_bts[asset] = []
  volume_in_bts[asset] = []
 ## BTC
 for asset in asset_list_publish :
  for priceBTC in price_in_btc[ asset ] :
   for idx in range(0, len(price_in_btc["BTS"])) :
    price_in_bts[asset].append( float("%.8g" % float(price_in_btc["BTS"][idx]/priceBTC)))
    volume_in_bts[asset].append(float("%.8g" % float(volume_in_btc["BTS"][idx]/priceBTC)))
 ## CNY
 for asset in asset_list_publish :
  for priceCNY in price_in_cny[ asset ] :
   for idx in range(0, len(price_in_cny["BTS"])) :
    price_in_bts[asset].append( float("%.8g" % float(price_in_cny["BTS"][idx]/priceCNY)))
    volume_in_bts[asset].append(float("%.8g" % float(volume_in_cny["BTS"][idx]/priceCNY)))
 ## USD
 for asset in asset_list_publish :
  for priceUSD in price_in_usd[ asset ] :
   for idx in range(0, len(price_in_usd["BTS"])) :
    price_in_bts[asset].append( float("%.8g" % float(price_in_usd["BTS"][idx]/priceUSD)))
    volume_in_bts[asset].append(float("%.8g" % float(volume_in_usd["BTS"][idx]/priceUSD)))
 ## EUR
 for asset in asset_list_publish :
  for priceEUR in price_in_eur[ asset ] :
   for idx in range(0, len(price_in_eur["BTS"])) :
    price_in_bts[asset].append( float("%.8g" % float(price_in_eur["BTS"][idx]/priceEUR)))
    volume_in_bts[asset].append(float("%.8g" % float(volume_in_eur["BTS"][idx]/priceEUR)))

 for asset in asset_list_publish :
  ### Median
  #price_in_bts_average[asset] = statistics.median(price_in_bts[asset])
  ### Mean
  #price_in_bts_average[asset] = statistics.mean(price_in_bts[asset])
  ### Weighted Mean
  volume     = [b for b in  volume_in_bts[asset] ]
  assetprice = [a for a in  price_in_bts[asset]  ]
  price_in_bts_weighted[asset] = num.average(assetprice, weights=volume)
  ### Discount
  price_in_bts_weighted[asset] = price_in_bts_weighted[asset] * config.discount

def print_stats() :
 t = PrettyTable(["asset","my price","my mean","my median","blockchain median","% change (my)","% change (blockchain)","std exchanges","% spread exchanges","last update"])
 t.align                   = 'r'
 t.border                  = True
 t.float_format['my price']            = ".8"
 t.float_format['my mean']             = ".8"
 t.float_format['my median']           = ".8"
 t.float_format['blockchain median']   = ".8"
 t.float_format['% change (my)']         = ".5"
 t.float_format['% change (blockchain)'] = ".5"
 t.float_format['std exchanges']         = ".5"
 t.float_format['% spread exchanges']    = ".5"
 #t.align['BTC']            = "r"
 for asset in asset_list_publish :
    weighted_external_price = price_in_bts_weighted[asset]
    prices_from_exchanges   = price_in_bts[asset]
    price_from_blockchain   = price_median_blockchain[asset]
    t.add_row([asset,\
               weighted_external_price, \
               statistics.mean(prices_from_exchanges),\
               statistics.median(prices_from_exchanges),\
               price_from_blockchain,\
               ((weighted_external_price - float(myCurrentFeed[asset]))/float(myCurrentFeed[asset]))*100,\
               ((weighted_external_price - price_from_blockchain)/price_from_blockchain)*100, \
               (statistics.stdev(prices_from_exchanges)),\
               (num.max(prices_from_exchanges)-num.min(prices_from_exchanges))/weighted_external_price*100,\
               (str(datetime.utcnow()-oldtime[asset]))\
              ])
 print(t.get_string())

## ----------------------------------------------------------------------------
## Run Script
## ----------------------------------------------------------------------------
if __name__ == "__main__":
 ## API header ################################################################
 headers = {'content-type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
 ## rpc variables about bts rpc ###############################################
 rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
 asset_list_all = ["BTC", "SILVER", "GOLD", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD", "KRW"]
 delegate_list  = config.delegate_list
 ## Call Parameters ###########################################################
 if len( sys.argv ) < 2 :
  sys.exit( "Usage: bts_feed.py <space separated list of currencies>" )
 else :
  if sys.argv[1] == "ALL":
   asset_list_publish = asset_list_all
  else :
   asset_list_publish = sys.argv
   asset_list_publish.pop(0)

 ## Initialization
 volume_in_cny           = {}
 volume_in_usd           = {}
 volume_in_btc           = {}
 volume_in_eur           = {}
 volume_in_bts           = {}
 price_in_cny            = {}
 price_in_usd            = {}
 price_in_btc            = {}
 price_in_eur            = {}
 price_in_bts            = {}
 price_in_bts_weighted   = {}
 volume                  = {}
 myCurrentFeed           = {}
 price_median_blockchain = {}
 realPrice               = {}
 assetprecision          = {}
 assetprecision["BTS"]   = 1e5
 oldtime                 = {}

 for asset in asset_list_all + ["BTS"]: 
  price_in_bts[ asset ]         = []
  price_in_eur[ asset ]          = []
  price_in_usd[ asset ]          = []
  price_in_btc[ asset ]          = []
  price_in_cny[ asset ]          = []
  volume_in_eur[ asset ]         = []
  volume_in_usd[ asset ]         = []
  volume_in_btc[ asset ]         = []
  volume_in_cny[ asset ]         = []
  volume_in_bts[ asset ]        = []
  price_in_bts_weighted[asset]  = 0.0
  myCurrentFeed[asset]           = 0.0
  price_median_blockchain[asset] = 0.0
  realPrice[asset]               = 0.0
  oldtime[asset]                 = datetime.utcnow()

 ## Get prices and stats ######################################################
 print("Loading data: ", end="",flush=True)
 fetch_from_wallet(rpc)
 print("yahoo", end="",flush=True)
 fetch_from_yahoo()
 print(", Yunbi", end="",flush=True)
 fetch_from_yunbi()
 print(", BTC38", end="",flush=True)
 fetch_from_btc38()
 print(", BTer", end="",flush=True)
 fetch_from_bter()
 print(", Poloniex", end="",flush=True)
 fetch_from_poloniex()
 print(", bittrex", end="",flush=True)
 fetch_from_bittrex()
 print(" -- done. Calculating bts feeds prices and checking publish rules.")

 ## Determine bts price ######################################################
 get_btsprice()

 ## Only publish given feeds ##################################################
 asset_list_final = []
 for asset in asset_list_publish :
  if len(price_in_bts[asset]) > 0 :
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
