#!/usr/bin/env python3
# coding=utf8 sw=1 expandtab ft=python

import os
import sys
from datetime import datetime
import time
from btsx import BTSX
from config import read_config
from bots import MarketMaker
from bots import MarketSpeculator
import exchanges as ex
import logging
import logging.handlers

## Loading Config
config = read_config(sys.argv[1])

## Setting up Logger
LOG_FILENAME = "logs/%s" % (config["log"])
log          = logging.getLogger('MarketMakerBot')
handler      = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes = config["logMaxByte"], backupCount = config["logBackupCnt"])
log.addHandler(handler)
log.setLevel(logging.INFO)

## Opening RPC to wallet
client = BTSX(
    config["client"]["rpc_user"],
    config["client"]["rpc_password"],
    config["client"]["rpc_host"],
    config["client"]["rpc_port"]
)

## Loading Exchanges
exchanges = ex.Exchanges(log)
exchanges.getAllPrices()
## Useful Variables from the exchanges object: ####################################################
# exchange.lastupdate     : Last time the prices have been updated
# exchange.assetprecision : precision of each asset as dict (capital letters asset)
# exchange.volume_incny   : volume calculated in CNY of each asset as dict (capital letters asset)
# exchange.volume_inusd   : volume calculated in USD of each asset as dict (capital letters asset)
# exchange.volume_inbtc   : volume calculated in BTC of each asset as dict (capital letters asset)
# exchange.volume_ineur   : volume calculated in EUR of each asset as dict (capital letters asset)
# exchange.volume_inbtsx  : volume calculated in BTSX of each asset as dict (capital letters asset)
# exchange.price_incny    : price of each asset (as dict) in CNY
# exchange.price_inusd    : price of each asset (as dict) in USD
# exchange.price_inbtc    : price of each asset (as dict) in BTC
# exchange.price_ineur    : price of each asset (as dict) in EUR
# exchange.price_inbtsx   : price of each asset (as dict) in BTSX
###################################################################################################

## Add Bots
bots = []
for botconfig in config["bots"]:
    bot_type = botconfig["bot_type"]
    if bot_type == "market_maker":
        bots.append(MarketMaker(client, exchanges, botconfig, log))
    elif bot_type == "market_speculator":
        ## FIXME this bot is not yet modified to with 'exchanges'
        bots.append(MarketSpeculator(client, exchanges, botconfig, log))
    else :
        raise Exception("unknown bot type: %s" % (bot_type))

while True:
    for bot in bots:
        bot.execute()
    time.sleep(10)
    if (datetime.utcnow()-exchanges.lastupdate).total_seconds() > config["maxAgePriceSec"] :
        log.info( "updating price from exchanges" )
        exchanges.getAllPrices()
