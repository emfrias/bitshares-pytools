#!/usr/bin/env python
# coding=utf8

import requests
import json
import sys

import datetime, threading, time
from pprint import pprint

headers = {'content-type': 'application/json',
   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

## -----------------------------------------------------------------------
## Load Config
## -----------------------------------------------------------------------
config_data = open('config.json')
config = json.load(config_data)
config_data.close()

## -----------------------------------------------------------------------
## function about bts rpc
## -----------------------------------------------------------------------
auth = (config["bts_rpc"]["username"], config["bts_rpc"]["password"])
url  = config["bts_rpc"]["url"]
asset_list_publish = sys.argv
asset_list_publish.pop(0)
asset_list_all = ["PTS", "PPC", "LTC", "BTC", "WTI", "SLV", "GLD", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD"]
delegate_list = config["delegate_list"]

def fetch_from_btc38():
  url="http://api.btc38.com/v1/ticker.php"
  try:
    ########################
    params = { 'c': 'btsx', 'mk_type': 'btc' }
    responce = requests.get(url=url, params=params, headers=headers)
    result = responce.json()
    price["BTC"].append(float(result["ticker"]["last"]))
    ########################
    params = { 'c': 'btsx', 'mk_type': 'cny' }
    responce = requests.get(url=url, params=params, headers=headers)
    result = responce.json()
    price_cny = float(result["ticker"]["last"])
    price["CNY"].append(price_cny)
    price["USD"].append(price_cny/rate_usd_cny)
    price["GLD"].append(price_cny/rate_xau_cny)
    price["EUR"].append(price_cny/rate_usd_cny*rate_eur_usd)
  except:
    print "Warning: unknown error"
    return

def fetch_from_bter():
  try:
    ########################
    url="http://data.bter.com/api/1/ticker/btsx_btc"
    responce = requests.get(url=url, headers=headers)
    result = responce.json()
    price["BTC"].append(float(result["avg"]))
    ########################
    url="http://data.bter.com/api/1/ticker/btsx_btc"
    responce = requests.get(url=url, headers=headers)
    result = responce.json()
    price["BTC"].append(float(result["avg"]))
    ########################
    url="http://data.bter.com/api/1/ticker/btsx_usd"
    responce = requests.get(url=url, headers=headers)
    result = responce.json()
    price_usd = float(result["avg"])
    price["USD"].append(price_usd)
    price["EUR"].append(price_usd*rate_eur_usd)
    ########################
    url="http://data.bter.com/api/1/ticker/btsx_cny"
    responce = requests.get(url=url, headers=headers)
    result = responce.json()
    price_cny = float(result["avg"])
    price["CNY"].append(price_cny)
    price["USD"].append(price_cny/rate_usd_cny)
    price["GLD"].append(price_cny/rate_xau_cny)
    price["EUR"].append(price_cny/rate_usd_cny*rate_eur_usd)
  except:
    print "Warning: unknown error"
    return

def fetch_from_poloniex():
  try:
    ########################
    url="https://poloniex.com/public?command=returnTicker"
    responce = requests.get(url=url, headers=headers)
    result = responce.json()
    price["BTC"].append(float(result["BTC_BTSX"]["last"]))
  except:
    print "Warning: unknown error"
    return

def fetch_from_bitrex():
  try:
    ########################
    url="https://bittrex.com/api/v1.1/public/getticker?market=BTC-BTSX"
    responce = requests.get(url=url, headers=headers)
    result = responce.json()
    price["BTC"].append(float(result["result"]["Last"]))
  except:
    print "Warning: unknown error"
    return

def get_rate_from_yahoo():
  global headers
  global rate_usd_cny, rate_xau_cny, rate_eur_usd
  try:
    url="http://download.finance.yahoo.com/d/quotes.csv"
    params = {'s':'USDCNY=X,XAUCNY=X,USDEUR=X','f':'l1','e':'.csv'}
    responce = requests.get(url=url, headers=headers,params=params)
    ####################
    pos = posnext = 0
    posnext = responce.text.find("\n", pos)
    rate_usd_cny = float(responce.text[pos:posnext])
    print "Fetch: rate usd/cny", rate_usd_cny
    ####################
    pos = posnext + 1
    posnext = responce.text.find("\n", pos)
    rate_xau_cny = float(responce.text[pos:posnext])
    print "Fetch: rate xau/cny", rate_xau_cny
    ####################
    pos = posnext + 1
    posnext = responce.text.find("\n", pos)
    rate_eur_usd = float(responce.text[pos:posnext])
    print "Fetch: rate usd/eur", rate_eur_usd
    ####################
  except:
    print "Warning: unknown error, try again after 1 seconds"
    time.sleep(1)
    get_rate_from_yahoo()

def convert_btc():
        url = "https://api.bitcoinaverage.com/ticker/USD/"
        responce = requests.get(url=url, headers=headers)
        result = responce.json()
        priceBTC = float(result["24h_avg"])
        for b in price["BTC"] :
         price["USD"].append(b*priceBTC)

        url = "https://api.bitcoinaverage.com/ticker/EUR/"
        responce = requests.get(url=url, headers=headers)
        result = responce.json()
        priceBTC = float(result["24h_avg"])
        for b in price["BTC"] :
         price["EUR"].append(b*priceBTC)

        url = "https://api.bitcoinaverage.com/ticker/CNY/"
        responce = requests.get(url=url, headers=headers)
        result = responce.json()
        priceBTC = float(result["24h_avg"])
        for b in price["BTC"] :
         price["CNY"].append(b*priceBTC)

def update_feed(assets):
  for delegate in delegate_list:
        headers = {'content-type': 'application/json'}
        request = {
            "method": "wallet_publish_feeds",
            "params": [delegate, assets],
            "jsonrpc": "2.0",
            "id": 1
            }
        while True:
          try:
            responce = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
            result = json.loads(vars(responce)["_content"])
            print "Update:", delegate, assets
          except:
            print "Warnning: Can't connect to rpc server, retry 5 seconds later"
            time.sleep(5)
            continue
          break

rate_usd_cny = 0.0
rate_xau_cny = 0.0
rate_eur_usd = 0.0
price = {}
price_average = {}
for asset in asset_list_all:
  price[asset] = []
  price_average[asset] = 0.0

print "Loading Yahoo"
get_rate_from_yahoo()
print "Loading BTC38"
fetch_from_btc38()
print "Loading BTer"
fetch_from_bter()
print "Loading Poloniex"
fetch_from_poloniex()
print "Loading bitrex"
fetch_from_bitrex()
print "converting btc to USD/CNY/EUR"
convert_btc()

asset_list_final = []
for asset in asset_list_publish:
   price_average[asset] = sum(price[asset])/len(price[asset])
   if price_average[asset] > 0.0:
     asset_list_final.append({ asset : price_average[asset] })
pprint( asset_list_final )
update_feed(asset_list_final)
