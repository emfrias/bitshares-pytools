import binascii
import Transactions
from pprint import pprint
import json

withdrawals = [
            {
                "balance_id":"BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh",
                "privkey"   :"5JA7KYYHX2jkHjhmMigpaRLJuQ3peGFpftR34Z7vMUso9hLwbrA",
                "amount"    : .1 * 1e5,
                "asset_id"  : 0
            },
            {
                "balance_id":"BTSG9SrG1qe2EtDbJkjbTUN4epSNG755P1y7",
                "privkey"   :"5JA7KYYHX2jkHjhmMigpaRLJuQ3peGFpftR34Z7vMUso9hLwbrA",
                "amount"    : 5*1e4,
                "asset_id"  : 21
            },
       ] 

receiveAddresses = [ 
        {
            "address" : "BTS8kXVZ6o1uZDnCkUaKgKVUaytFSFespzWm",
            "amount"  : 1.0 * 1e4,
            "asset_id": 21
        },
        {
            "address" : "BTS9NArckpAesJLQVJP42yzpp1D7RahyjaL7",
            "amount"  : 1.0 * 1e4,
            "asset_id": 21
        },
        {
            "address" : "BTSFweqCSFv2seFPsLxjp6eWXwCkN66uxesx",
            "amount"  : 1.0 * 1e4,
            "asset_id": 21
        },
        {
            "address" : "BTSNtJPSq8ejj9CtBK5YnkVKEBxmXK5TZW12",
            "amount"  : 1.0 * 1e4,
            "asset_id": 21
        },
        {
            "address" : "BTS22qUEF6TT5yL7SwkvU4hdMtK2zZEAGmeZ",
            "amount"  : 1.0 * 1e4,
            "asset_id": 21
        },
        ]
otk            = None
slate_id       = 0   # no slate
fee            = .1 * 1e5

ops = []
privkeys = []
### Withdraw Fee in BTS!
for w in withdrawals :
    withdraw = Transactions.Withdraw( w["balance_id"], w["amount"])
    ops.append(Transactions.Operation( "withdraw_op_type", withdraw ))
    privkeys.append(w["privkey"])

for d in receiveAddresses :
    wst      = Transactions.WithdrawSignatureType( d[ "address" ] )
    wc       = Transactions.WithdrawCondition( d["asset_id"], slate_id, "withdraw_signature_type", wst)
    deposit  = Transactions.Deposit( d["amount"], wc )
    ops.append(Transactions.Operation( "deposit_op_type", deposit))

tx       = Transactions.Transaction( 60*60*24, 0, ops )
sigtx    = Transactions.SignedTransaction(tx, privkeys)

pprint(sigtx.tojson())
print(binascii.hexlify(sigtx.towire()))
print(json.dumps(sigtx.tojson()).replace(" ", ""))

pprint( {"expiration":"2015-02-23T20:03:38","slate_id":"null","operations":[{"type":"withdraw_op_type","data":{"balance_id":"BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh","amount":"10000","claim_input_data":""}},{"type":"withdraw_op_type","data":{"balance_id":"BTSG9SrG1qe2EtDbJkjbTUN4epSNG755P1y7","amount":"50000","claim_input_data":""}},{"type":"deposit_op_type","data":{"amount":"10000","condition":{"asset_id":-11,"slate_id":"0","type":"withdraw_signature_type","data":{"owner":"BTS8kXVZ6o1uZDnCkUaKgKVUaytFSFespzWm"}}}},{"type":"deposit_op_type","data":{"amount":"10000","condition":{"asset_id":-11,"slate_id":"0","type":"withdraw_signature_type","data":{"owner":"BTS9NArckpAesJLQVJP42yzpp1D7RahyjaL7"}}}},{"type":"deposit_op_type","data":{"amount":"10000","condition":{"asset_id":-11,"slate_id":"0","type":"withdraw_signature_type","data":{"owner":"BTSFweqCSFv2seFPsLxjp6eWXwCkN66uxesx"}}}},{"type":"deposit_op_type","data":{"amount":"10000","condition":{"asset_id":-11,"slate_id":"0","type":"withdraw_signature_type","data":{"owner":"BTSNtJPSq8ejj9CtBK5YnkVKEBxmXK5TZW12"}}}},{"type":"deposit_op_type","data":{"amount":"10000","condition":{"asset_id":-11,"slate_id":"0","type":"withdraw_signature_type","data":{"owner":"BTS22qUEF6TT5yL7SwkvU4hdMtK2zZEAGmeZ"}}}}],"signatures":["1ffed7121f9a10f4cae28c84ed9b414a94e41ac8edf16d436eae3b1d85193173ede5ab780a3e5ab3454467ddced840872ff45ae9d2a4e053fc75f152ca8e29e145"]} )
pprint(sigtx.tojson())

print(json.dumps(sigtx.tojson()).replace(" ", ""))

#{"trx":{"operations":[{"type":"withdraw_op_type","data":{"claim_input_data":"","balanceid":"BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh","amount":10000}},{"type":"withdraw_op_type","data":{"claim_input_data":"","balanceid":"BTSG9SrG1qe2EtDbJkjbTUN4epSNG755P1y7","amount":50000}},{"type":"deposit_op_type","data":{"amount":10000,"condition":{"asset_id":21,"slate_id":0,"type":"withdraw_signature_type","data":{"owner":"BTS8kXVZ6o1uZDnCkUaKgKVUaytFSFespzWm","memo":{}}}}},{"type":"deposit_op_type","data":{"amount":10000,"condition":{"asset_id":21,"slate_id":0,"type":"withdraw_signature_type","data":{"owner":"BTS9NArckpAesJLQVJP42yzpp1D7RahyjaL7","memo":{}}}}},{"type":"deposit_op_type","data":{"amount":10000,"condition":{"asset_id":21,"slate_id":0,"type":"withdraw_signature_type","data":{"owner":"BTSFweqCSFv2seFPsLxjp6eWXwCkN66uxesx","memo":{}}}}},{"type":"deposit_op_type","data":{"amount":10000,"condition":{"asset_id":21,"slate_id":0,"type":"withdraw_signature_type","data":{"owner":"BTSNtJPSq8ejj9CtBK5YnkVKEBxmXK5TZW12","memo":{}}}}},{"type":"deposit_op_type","data":{"amount":10000,"condition":{"asset_id":21,"slate_id":0,"type":"withdraw_signature_type","data":{"owner":"BTS22qUEF6TT5yL7SwkvU4hdMtK2zZEAGmeZ","memo":{}}}}}],"slate_id":0,"expiration":1424722231},"signatures":["20fb36a393b49b55179fb9f0c82949e092a0d8f8dca180cf56c4a552f2502aba415d57287b3e2f6eb3b17bb8e17687507fe7aa7557f73aff3ab83991941aa664d2"]}

