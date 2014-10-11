#!/usr/bin/env python3
# coding=utf8 sw=1 expandtab ft=python

import sys
from datetime import datetime
import time
from btsx import BTSX
from config import read_config
from bots import MarketMaker
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

## Loading Exchanges
exchanges = ex.Exchanges(log)
exchanges.getAllPrices()

## Opening RPC to wallet
client = BTSX(
    config["client"]["rpc_user"],
    config["client"]["rpc_password"],
    config["client"]["rpc_port"]
)

## Add Bots
bots = []
for botconfig in config["bots"]:
    bot_type = botconfig["bot_type"]
    if bot_type == "market_maker":
        bots.append(MarketMaker(client, exchanges, botconfig, log))
    elif bot_type == "market_speculator":
        ## FIXME this bot is not yet modified to with 'exchanges'
        #bots.append(MarketSpeculator(client, exchanges, botconfig, log))
    else:
        raise Exception("unknown bot type")

while True:
    for bot in bots:
        bot.execute()
    time.sleep(10)
    if (datetime.utcnow()-exchanges.lastupdate).total_seconds() > config["maxAgePriceSec"] :
        log.info( "updating price from exchanges" )
        exchanges.getAllPrices()
