# What is this? #

This repository contains several tools (mostly written in Python2) that
interact with the official BitShares client via RPC and perform certain tasks.

The following libraries are costum made and part of this repository as
submodules.
* **python-bitsharesrpc**: Connect to the BitShares client via RPC
* **python-bitsharestools**: BitShares tools such as Address derivation, Transaction contstruction, Paperwallets, ...

Some scripts are intended for delegates, such as:
* **delegate-feed**: Script that can be run via cron in order to derive a feed price and publish the price for your delegate(s)
* **delegate-slate**: Construct and deploy a slate for your delegate(s)
* **delegate-payouts**: Perform DEX (decentralized exchange) tasks with the funds payed to your delegate
* **delegate-changetosigningkeysonly**: Change the signing key of your delegate(s) for security reasons
* **delegate-switchover**: Switch over to a second machine to produce blocks (usable during software upgrades)

User scripts
* **paperwallet**: Different tools to construct PDF paperwallets
* **papersharedrop**: Sharedrop assets onto paperwallets (for meetups etc)
* **coldstorage**: Tools for cold storage
* **user-tonewactivekey**: Change the active key of any of your accounts so you can put your owner keys in cold storage
* **marketbots**: Bots to run the decentralized market exchange
* **tools**: Various maintainance tools

# Installation #
None of the tools require installation. However, they require the
python-bitsharesrpc module in order to interact with the client via RPC. Some
other scripts require the python-bitsharestools module to be installed.

In order to install the modules you need to update the git submodules. The
easiest way to install the module goes as:

    git submodule init
    git submodule update

## python-bitsharesrpc ##

Connections to the BitShares client are performed using the python-bitsharesrpc
package. The original sources for the bitsharesrpc package are located at

* https://github.com/xeroc/python-bitsharesrpc

Installtion:

    cd python-bitsharesrpc
    python setup.py install --user

A detailed README for the bitsharesrpc package can be found in the package
subdirectory: `bitshares-pytools/python-bitsharesrpc/README.md`

## python-bitsharestools ##

Offers low-level tools for BitShares, such as address convertion and transaction
construction.

* https://github.com/xeroc/python-bitsharestools

Installtion:

    cd python-bitsharestools
    python setup.py install --user

A detailed README for the bitsharestools package can be found in the package
subdirectory: `bitshares-pytools/python-bitsharestools/README.md`

# Configuration #

Most subfolders require their own `config.py`. Example configuration can be
found as `config-sample.py` and are required to be stored in a file called
`config.py`. The basic configuration in order to connect to the bitshares
client is:

    url    = "http://localhost:19988/rpc"
    user   = 'username'
    passwd = 'pwd'
    unlock = "unlockPwd"
    wallet = "default"

Individual tools may require more parameters to be set. Please take a look at
the `config-example.py` in the corresponding folders.

# DISCLAIMER: #
- I used this to learn how to write python code
- don't use with serious money unless you know what you are doing and checked the code

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
