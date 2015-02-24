#!/usr/bin/env python2
import binascii
import Transactions
from pprint import pprint
import json
import bitsharesrpc
import config

chainid        = "75c11a81b7670bbaa721cc603eadb2313756f94a3bcbb9928e9101432701ac5f"
PREFIX         = "BTS"
receiveAddress = "BTSPZDA4bH9mQddS8pm3mcmVDU7pnwatUEyo"
balance_id     = "BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh"
privKey        = "5JA7KYYHX2jkHjhmMigpaRLJuQ3peGFpftR34Z7vMUso9hLwbrA"
otk            = None
asset_id       = 0   # BTS
slate_id       = None   # no slate
fee            = .1 * 1e5
amount         = 1*1e5 - fee

### Withdraw Transaction -- equals BTC input
withdraw = Transactions.Withdraw( balance_id, amount+fee)

### Deposit Transaction -- equals BTC outputs
wst      = Transactions.WithdrawSignatureType( receiveAddress )
wc       = Transactions.WithdrawCondition( asset_id, "0", "withdraw_signature_type", wst)
deposit  = Transactions.Deposit( amount, wc )

### Combine Operations (possibly more)
ops = []
ops.append(Transactions.Operation( "deposit_op_type", deposit))
ops.append(Transactions.Operation( "withdraw_op_type", withdraw ))

### Construct and sign Transaction
tx       = Transactions.Transaction( 60*60*12, slate_id, ops )
sigtx    = Transactions.SignedTransaction(tx, [privKey])

## Send operation
rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
print(rpc.blockchain_broadcast_transaction(sigtx.tojson()))
