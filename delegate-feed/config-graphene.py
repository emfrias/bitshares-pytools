################################################################################
## RPC-client connection information (required)
################################################################################
network = "graphene"
url    = "http://127.0.0.1:8093/"
user   = "" # not used for graphene
passwd = "" # not used for graphene

# password for automatically unlocking the wallet immediately before publishing a feed, 
# if you choose to leave your wallet locked 
unlock = "my_password"
wallet = "" # not used for graphene

################################################################################
## Delegate Feed Publish Parameters
################################################################################
feed_producer_list   = [ "my-account", ] # a list of account names authorized to produce feeds via update_asset_feed_producers()
assets_to_feed = { "BTC" : "MINE.BTC" } #, "USD": "MINE.USD", "CNY": "MINE.CNY" } # a dictionary mapping 'common coin symbol' -> 'market issued asset on graphene' 
coreExchangeRateMultiplier = 1.0 # If you set this to > 1.0, you will profit when people use the fee pool instead of paying the fees themselves
maintenanceCollateralRatio = 1750 # Call when collateral only pays off 175% the debt (1750 is the default value)
maxShortSqueezeRatio = 1500 # Stop calling when collateral only pays off 150% of the debt (1500 is the default value)

maxAgeFeedInSeconds  = 1200
minValidAssetPrice   = 0.00001
discount             = 0.995
change_min           = 0.5
btc38_trust_level    = 0.7
bter_trust_level     = 1.0
poloniex_trust_level = 0.5
bittrex_trust_level  = 0.5
yunbi_trust_level    = 0.5
