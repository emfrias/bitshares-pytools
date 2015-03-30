# What is this #

This tool will sharedrop an arbitrary amount amount/symbol pairs into an
(almost) arbitrary amount of address/privkey pair.
You can use this to preload paperwallets for meetups and conferences.

# Howto use #

* Open your BitShares client
* Get a new address to use for funding the wallets (say `BTS-address`) with
    
    wallet_address_create <account>
* Send the funds you want to distribute to that address (the client will figure
  out the private key for that address by asking the client)
* Define the RPC connection in `config.py` (see example in `config-example.py`)
* Run the sharedrop script like this

    python2 sharedrop.py <address_with_funds> <number_of_wallets> "<amount-asset-pair>" ["<amount-asset-pair>"]

# Examples #

    python2 sharedrop.py BTSPFjktNqSUadcATtCzMm3zn1LmQystnX3B 10 "1 NOTE"

    python2 sharedrop.py BTSPFjktNqSUadcATtCzMm3zn1LmQystnX3B 10 "1 USD" "0.5 BTS"

    python2 sharedrop.py BTSPFjktNqSUadcATtCzMm3zn1LmQystnX3B 5 "1 USD" "1 NOTE" "1 BTS"
