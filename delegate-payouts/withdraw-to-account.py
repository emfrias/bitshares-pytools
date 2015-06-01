#!/usr/bin/python
import bitsharesrpc
import config
import re

withdrawfee = 0.1 * 1e5;

rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
rpc.wallet_open(config.wallet)
rpc.unlock(999999,config.unlock)

# Withdraw delegate pay #############################################
print("-"*80)
print("| Withdrawing delegate pay")
print("-"*80)
account = rpc.wallet_get_account(config.accountname)["result"]
assert "delegate_info" in account, "Account %s not registered as delegate" % config.accountname
if float(account["delegate_info"]["pay_balance"]) < config.withdrawlimit*config.btsprecision :
 print "Not enough pay to withdraw yet!"
else :
 payout = float(account["delegate_info"]["pay_balance"]) - config.txfee*config.btsprecision
 print "Withdrawing %10.5f BTS from %s to %s" % (account["delegate_info"]["pay_balance"]/config.btsprecision,account["name"], config.exchangename)
 ret = rpc.wallet_delegate_withdraw_pay(account["name"],config.exchangename,str((payout/config.btsprecision)), "auto pay day") 

rpc.lock()
