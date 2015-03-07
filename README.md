# What is this? #

This repository contains several tools (mostly written in Python2) that interact
with the official BitShares client via RPC and perform certain tasks. Most
prominently:

* **python-bitsharesrpc**: Submodule required by most tools (see Installation below) to connect to the BitShares client
* **delegate-feed** (for delegates): script that can be run via cron in order to derive a feed price and publish the price for your delegate(s)
* **delegate-slate** (for delegates): Construct and deploy a slate for your delegate(s)
* **delegate-payouts** (for delegates): Perform DEX (decentralized exchange) tasks with the funds payed to your delegate
* **delegate-changetosigningkeysonly** (for delegates): Change the signing key of your delegate(s) for security reasons
* **switchoverdelgate** (for delegates): Switch over to a second machine to produce blocks (usable during software upgrades)
* **user-tonewactivekey**: Change the active key of any of your accounts so you can put your owner keys in cold storage
* **Transactions**: Transaction construction class (demo inside)
* **tools**: Various maintainance tools

# Installation #
None of the tools require installation. However, they require the
python-bitsharesrpc module in order to interact with the client via RPC.

## python-bitsharesrpc ##

Connections to the BitShares client are performed using the python-bitsharesrpc
package. The original sources for the bitsharesrpc package are located at

* https://github.com/xeroc/python-bitsharesrpc

In order to install the python-bitsharesrpc package you need to update the
submodule. The easiest way to install the module goes as:

    git submodule init
    git submodule update
    cd python-bitsharesrpc
    python setup.py install    # (optionally with parameter --user fo non-root installations)

A detailed README for the bitsharesrpc package can be found in the package
subdirectory: `bitshares-pytools/python-bitsharesrpc/README.md`

# Configuration #

Every subfolder requires it's own `config.py`. An example configuration can be
found in `config-sample.py` and are required to be stored in a file called
`config.py`. The basic configuration in order to connect to the bitshares
client is:

    url    = "http://localhost:19988/rpc"
    user   = 'username'
    passwd = 'pwd'
    unlock = "unlockPwd"
    wallet = "default"

Individual tools may require more parameters to be set. Please take a look at
the `config-example.py` in the corresponding folders.
