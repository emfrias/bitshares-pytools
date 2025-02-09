# Cold Storage Solution for BitShares #

## What is this? ##
This is a set of tools for cold storage and offline signing of balance
transactions, i.e., withdraw funds from a cold storage address and putting them
into a hot wallet (address).

## Requirements ##
 * python-bitsharesrpc (for online part)
 * python-bitsharestools (for offline signin)
 * (optional) python2-qrtools (for QR-code support)

## What parts are there and what are they doing? ##
Two parts:

### `online` ###
Just get the balances stored in the cold storage address.

**Help:**

    usage: python2 online.py [-h] [--filename FILENAME] [--rpcurl RPCURL] [--rpcuser RPCUSER] [--rpcpasswd RPCPASSWD] coldaddress

**Example:**

    $ python2 online.py BTS4CNbXqeEym7JopKYvL16qVKUe9kRMMC8x
    Available Funds in cold storage address BTS4CNbXqeEym7JopKYvL16qVKUe9kRMMC8x
    - 5.000000 EUR
    - 0.000000 BTS
    Stored funds for 2 assets in 'availablefunds.txt' for offline construction & signing."

By default writes a txt file `availablefunds.txt` to the current directoy. This
file has to be moved to the offline computer for construction of the
transaction and signing process.

### `offline` ###
Take the balance file from the `online` tool, ask for amount and assets to
transfer to the deposit address. The private key for signing is required in a
separated step and can be read by QR-code scanner. Note that only
one private key (i.e. one cold storage address) can be accessed at a time.
This script returns a readable (JSON formated) and signed transaction
instruction that can be pasted into the console of a connected BitShares
client. The signed transaction is also stored in a file `signedtx.txt` by
default.

**Help:**

        usage: python2 offline.py [-h] [--filename FILENAME] [--txfee TXFEE] [--address ADDRESS] [--prefix PREFIX] [--output OUTPUT]

**Example:**

    $ python2 offline.py --address BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh
    Available funds:
    5.000000 EUR
    0.500000 BTS
    Give amount AND asset [10 BTS]: 5 EUR
    Going to withdraw:
    5.000000 EUR
    Want more? [Y/n] n
    Adding tx fee of 0.500000 BTS
    Please type private key [empty for QR scanner]: 5**************************************************
    This private key gives access to funds in address BTS*********************************
    --------------------------------------------------------------------------------
    + Raw and signed transaction for verification:
    --------------------------------------------------------------------------------
    {
    "operations": [
        {
        "type": "withdraw_op_type", 
        "data": {
            "claim_input_data": "", 
            "amount": "50000", 
            "balance_id": "BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh"
        }
        }, 
        {
        "type": "withdraw_op_type", 
        "data": {
            "claim_input_data": "", 
            "amount": "50000", 
            "balance_id": "BTSG9SrG1qe2EtDbJkjbTUN4epSNG755P1y7"
        }
        }, 
        {
        "type": "deposit_op_type", 
        "data": {
            "amount": "50000", 
            "condition": {
            "asset_id": 21, 
            "slate_id": null, 
            "type": "withdraw_signature_type", 
            "data": {
                "owner": "BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh", 
                "memo": null
            }
            }
        }
        }
    ], 
    "slate_id": 0, 
    "signatures": [
        "202315d908cfd96eb43ba003d0efbaa02ca9584c79dca1474ed4bc1511bbedbed1ce29bfa0e98f8b78dcabd9c127c50bda18f7d26d5b9f70f0a03bc3f9096f122f"
    ], 
    "expiration": "2015-03-19T08:23:15"
    }
    --------------------------------------------------------------------------------
    + stripped output of signed transaction (issue this command in the BTS console):
    --------------------------------------------------------------------------------
    blockchain_broadcast_transaction {'operations':[{'type':'withdraw_op_type','data':{'claim_input_data':'','amount':'50000','balance_id':'BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh'}},{'type':'withdraw_op_type','data':{'claim_input_data':'','amount':'50000','balance_id':'BTSG9SrG1qe2EtDbJkjbTUN4epSNG755P1y7'}},{'type':'deposit_op_type','data':{'amount':'50000','condition':{'asset_id':21,'slate_id':None,'type':'withdraw_signature_type','data':{'owner':'BTSUTgrMqNAGqvhCJdYtuqVGkTCjP7ss3bh','memo':None}}}}],'slate_id':0,'signatures':['202315d908cfd96eb43ba003d0efbaa02ca9584c79dca1474ed4bc1511bbedbed1ce29bfa0e98f8b78dcabd9c127c50bda18f7d26d5b9f70f0a03bc3f9096f122f'],'expiration':'2015-03-19T08:23:15'}
    --------------------------------------------------------------------------------
    + signed transaction stored in file signedtx.txt
    --------------------------------------------------------------------------------

### Broadcasting ###

The default behavior is to load the RPC configuration from `config.py` and
broadcast the content of `signedtx.txt` to the BitShares network.

**Help:**

    usage: broadcast_signed_tx.py [-h] [--filename FILENAME] [--rpcurl RPCURL] [--rpcuser RPCUSER] [--rpcpasswd RPCPASSWD]

**Example:**

    python broadcast_signed_tx.py

## What's the procedure? ##
### Online ###
1. Go into the `online` part of the program and define the connection parameters to a running BitShares client in the `config.py` file
2. Get your cold storage address and either put it into the `config.py` file or append it to the command with "--address BTS...."
3. Run the `online` part of the program (it will list the funds stored in the cold storage address)

### Offline ###
1. Copy the balance file from the online tool over to the offline computer
2. Execute the `offline` program and optionally give the file name as parameter (see `python2 offline.py -h` for help)
3. Define the amount and asset you want to withdraw from the cold storage address
4. Paste the recipient address (or scan it with a webcam as QR-code)
5. Paste the private key (or scan it with a webcam as QR-code) -- The private key will be verified prior to signing.
6. The `offline` program constructs and signs a BitShares transaction 
7. Carry over the signed transaction file and execute `broadcast_signed_tx.py` on the online computer
8. Wait for 1 confirmation.
9. Done

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
