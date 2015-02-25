################################################################################
## RPC-client connection information (required)
################################################################################
url    = "http://localhost:19988/rpc"
user   = ""
passwd = ""
unlock = ""
wallet = ""

################################################################################
## Trusted delegates for slate (required for delegate-slate)
################################################################################
slatedelegate = "delegate-name"
slatepayee    = "paying-account"
trusted = [
 "delegate.charity",
 "a.delegate.charity",
 "delegate.xeroc"
]
