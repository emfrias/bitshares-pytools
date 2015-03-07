################################################################################
## RPC-client connection information (required)
################################################################################
url    = "http://localhost:19988/rpc"
user   = ""
passwd = ""
unlock = ""
wallet = ""

## Balance IDs ( DO NOT MIX THIS WITH ADDRESSES )
balanceids = [
                "BTSxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",   # BTS for fees
                "BTSxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",   # USD to sharedrop
              ] 

numberpaperwallets = 10   # The full amount in the balance id will be equally distributed
txfee              = 0.5  # The fee will be payed by the other balance id
