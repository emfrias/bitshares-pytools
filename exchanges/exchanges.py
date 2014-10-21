import requests
import json
from datetime import datetime
import time
import statistics
import re
from math import fabs
import numpy as num


class Exchanges() :

    ## ----------------------------------------------------------------------------
    ## Init
    ## ----------------------------------------------------------------------------
    def __init__(self,log):
         self.header = {'content-type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

         self.assets = ["PTS", "PPC", "LTC", "BTC", "SLV", "GLD", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD"] #  "WTI" missing as incompatible
         self.log = log
         self.lastupdate             = datetime.utcnow()
         self.volume_incny           = {}
         self.volume_inusd           = {}
         self.volume_inbtc           = {}
         self.volume_ineur           = {}
         self.volume_inbtsx          = {}
         self.price_incny            = {}
         self.price_inusd            = {}
         self.price_inbtc            = {}
         self.price_ineur            = {}
         self.price_inbtsx           = {}
         self.assetprecision          = {}
         self.assetprecision["BTSX"]  = 1e5

         for asset in self.assets + ["BTSX"]: 
             self.price_inbtsx[asset]         = []
             self.price_ineur[asset]          = []
             self.price_inusd[asset]          = []
             self.price_inbtc[asset]          = []
             self.price_incny[asset]          = []
             self.volume_ineur[asset]         = []
             self.volume_inusd[asset]         = []
             self.volume_inbtc[asset]         = []
             self.volume_incny[asset]         = []
             self.volume_inbtsx[asset]        = []

         self.price_inbtsx["BTSX"].append(1.0)
         self.price_ineur["EUR"].append(1.0)
         self.price_inusd["USD"].append(1.0)
         self.price_inbtc["BTC"].append(1.0)
         self.price_incny["CNY"].append(1.0)

    ## ----------------------------------------------------------------------------
    ## Fetch data
    ## ----------------------------------------------------------------------------
    ###########################################################################
    def fetch_from_btc38(self):
      url="http://api.btc38.com/v1/ticker.php"
      availableAssets = [ "LTC", "BTSX", "PTS" ]
      try :
       params = { 'c': 'all', 'mk_type': 'btc' }
       response = requests.get(url=url, params=params, headers=self.header)
       result = response.json()
      except: 
       self.log.error("Error fetching results from btc38!")
       return

      for coin in availableAssets :
       if "ticker" in result[coin.lower()] and result[coin.lower()]["ticker"] :
        self.price_inbtc[ coin ].append(float(result[coin.lower()]["ticker"]["last"]))
        self.volume_inbtc[ coin ].append(float(result[coin.lower()]["ticker"]["vol"]*result[coin.lower()]["ticker"]["last"]))

      availableAssets = [ "LTC", "BTSX", "BTC", "PPC", "PTS" ]
      try :
       params = { 'c': 'all', 'mk_type': 'cny' }
       response = requests.get(url=url, params=params, headers=self.header)
       result = response.json()
      except: 
       self.log.error("Error fetching results from btc38!")
       return

      for coin in availableAssets :
       if "ticker" in result[coin.lower()] and result[coin.lower()]["ticker"] :
        self.price_incny[ coin ].append(float(result[coin.lower()]["ticker"]["last"]))
        self.volume_incny[ coin ].append(float(result[coin.lower()]["ticker"]["vol"])*float(result[coin.lower()]["ticker"]["last"]))
    ###########################################################################
    def fetch_from_bter(self):
      try :
       url="http://data.bter.com/api/1/tickers"
       response = requests.get(url=url, headers=self.header)
       result = response.json()
      except:
       self.log.error("Error fetching results from bter!")
       return

      availableAssets = [ "LTC", "BTSX", "PTS", "PPC" ]
      for coin in availableAssets :
       self.price_inbtc[ coin ].append(float(result[coin.lower()+"_btc"]["last"]))
       self.volume_inbtc[ coin ].append(float(result[coin.lower()+"_btc"]["vol_btc"]))

      availableAssets = [ "BTC",  "LTC", "BTSX" ]
      for coin in availableAssets :
       self.price_inusd[ coin ].append(float(result[coin.lower()+"_usd"]["last"]))
       self.volume_inusd[ coin ].append(float(result[coin.lower()+"_usd"]["vol_usd"]))

      availableAssets = [ "BTSX", "BTC", "LTC", "BTSX", "PTS", "PPC" ]
      for coin in availableAssets :
       self.price_incny[ coin ].append(float(result[coin.lower()+"_cny"]["last"]))
       self.volume_incny[ coin ].append(float(result[coin.lower()+"_cny"]["vol_cny"]))

    ###########################################################################
    def fetch_from_poloniex(self):
      try:
       url="https://poloniex.com/public?command=returnTicker"
       response = requests.get(url=url, headers=self.header)
       result = response.json()
       availableAssets = [ "LTC", "BTSX", "PTS", "PPC" ]
      except:
       self.log.error("Error fetching results from poloniex!")

      for coin in availableAssets :
       self.price_inbtc[ coin ].append(float(result["BTC_"+coin.upper()]["last"]))
       self.volume_inbtc[ coin ].append(float(result["BTC_"+coin.upper()]["baseVolume"]))

    ###########################################################################
    def fetch_from_bitrex(self):
      availableAssets = [ "BTSX", "LTC", "BTSX", "PTS", "PPC" ]
      try:
       url="https://bittrex.com/api/v1.1/public/getmarketsummaries"
       response = requests.get(url=url, headers=self.header)
       result = response.json()["result"]
      except:
       self.log.error("Error fetching results from bitrex!")

      for coin in result :
       if( coin[ "MarketName" ] in ["BTC-"+a for a in availableAssets] ) :
        mObj    = re.match( 'BTC-(.*)', coin[ "MarketName" ] )
        altcoin = mObj.group(1)
        self.price_inbtc[ altcoin ].append(float(coin["Last"]))
        self.volume_inbtc[ altcoin ].append(float(coin["Volume"])*float(coin["Last"]))

    ###########################################################################
    def fetch_from_yahoo(self):
      try :
       availableAssets = ["XAG", "XAU", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD"]
       ## USD/X
       yahooAssets = ",".join(["USD"+a+"=X" for a in availableAssets])
       url="http://download.finance.yahoo.com/d/quotes.csv"
       params = {'s':yahooAssets,'f':'l1','e':'.csv'}
       response = requests.get(url=url, headers=self.header,params=params)
       yahooprices =  response.text.split( '\r\n' )
       for i,a in enumerate(availableAssets,1) :
        self.price_inusd[ self.bitassetname(a.upper()) ].append(1/float(yahooprices[i-1])) # flipped market
       ## CNY/X
       yahooAssets = ",".join([a+"CNY=X" for a in availableAssets])
       url="http://download.finance.yahoo.com/d/quotes.csv"
       params = {'s':yahooAssets,'f':'l1','e':'.csv'}
       response = requests.get(url=url, headers=self.header,params=params)
       yahooprices =  response.text.split( '\r\n' )
       for i,a in enumerate(availableAssets,1) :
        self.price_incny[ self.bitassetname(a.upper()) ].append(float(yahooprices[i-1])) ## market is the other way round! (yahooAssets)
       ## EUR/X
       yahooAssets = ",".join(["EUR"+a+"=X" for a in availableAssets])
       url="http://download.finance.yahoo.com/d/quotes.csv"
       params = {'s':yahooAssets,'f':'l1','e':'.csv'}
       response = requests.get(url=url, headers=self.header,params=params)
       yahooprices =  response.text.split( '\r\n' )
       for i,a in enumerate(availableAssets,1) :
        self.price_ineur[ self.bitassetname(a.upper()) ].append(float(yahooprices[i-1]))
      except: 
       self.log.error("Error fetching results from yahoo!")
       return

    ## ----------------------------------------------------------------------------
    ## GLD=XAU  SLV=XAG
    ## ----------------------------------------------------------------------------
    def bitassetname(self,asset) :
     if asset == "XAU" : 
      return "GLD"
     elif asset == "XAG" : 
      return "SLV"
     else :
      return asset

    ###########################################################################
    def getassetprecision(self):
     ## asset definition - mainly for precision
     for asset in self.assets :
      self.header = {'content-type': 'application/json'}
      request = {
        "method": "blockchain_get_asset",
        "params": [asset],
        "jsonrpc": "2.0", "id": 1 }
      response = requests.post(url, data=json.dumps(request), headers=self.header, auth=auth)
      result = response.json()
      self.assetprecision[asset] = float(result["result"]["precision"])

    ## ----------------------------------------------------------------------------
    ## calculate feed prices in BTSX for all assets given the exchange prices in USD,CNY,BTC
    ## ----------------------------------------------------------------------------
    def get_btsxprice(self):
     for asset in self.assets :
      self.price_inbtsx[asset] = []
      self.volume_inbtsx[asset] = []
     ## BTC
     for asset in self.assets :
      for priceBTC in self.price_inbtc[ asset ] :
       for idx in range(0, len(self.price_inbtc["BTSX"])) : # Price
        self.price_inbtsx[asset].append( float("%.8g" % float(self.price_inbtc["BTSX"][idx]/priceBTC)))
        self.volume_inbtsx[asset].append(float("%.8g" % float(self.volume_inbtc["BTSX"][idx]/priceBTC)))
     ## CNY
     for asset in self.assets :
      for priceCNY in self.price_incny[ asset ] :
       for idx in range(0, len(self.price_incny["BTSX"])) : # Price
        self.price_inbtsx[asset].append( float("%.8g" % float(self.price_incny["BTSX"][idx]/priceCNY)))
        self.volume_inbtsx[asset].append(float("%.8g" % float(self.volume_incny["BTSX"][idx]/priceCNY)))
     ## USD
     for asset in self.assets :
      for priceUSD in self.price_inusd[ asset ] :
       for idx in range(0, len(self.price_inusd["BTSX"])) : # Price
        self.price_inbtsx[asset].append( float("%.8g" % float(self.price_inusd["BTSX"][idx]/priceUSD)))
        self.volume_inbtsx[asset].append(float("%.8g" % float(self.volume_inusd["BTSX"][idx]/priceUSD)))
     ## EUR
     for asset in self.assets :
      for priceEUR in self.price_ineur[ asset ] :
       for idx in range(0, len(self.price_ineur["BTSX"])) : # Price
        self.price_inbtsx[asset].append( float("%.8g" % float(self.price_ineur["BTSX"][idx]/priceEUR)))
        self.volume_inbtsx[asset].append(float("%.8g" % float(self.volume_ineur["BTSX"][idx]/priceEUR)))

    ### Get prices and stats ######################################################
    def getAllPrices(self) :
        self.log.info("yahoo")
        self.fetch_from_yahoo()
        self.log.info("BTC38")
        self.fetch_from_btc38()
        self.log.info("BTer")
        self.fetch_from_bter()
        self.log.info("Poloniex")
        self.fetch_from_poloniex()
        self.log.info("bittrex")
        self.fetch_from_bitrex()
        self.log.info("Price Calculations.")
        self.get_btsxprice()
        self.lastupdate = datetime.utcnow()
