## What's this ##
These tools generate (encrypted) paperwallets as SVG or PDF

## Requirements ##
The following python libaries are required:
* csv
* qrcode
* lxml

For BIP38 encrypted paperwallets:
* python2-pybitcointools
* python2-scrypt

For PDF support
* svg2pdf
* PyPDF2

## Features ##
The following images and text boxes are individually replaced:
* QR code for address
* QR code for private key
* Address as text
* Amount
* Asset logo

## Example ##

### `genpaperwallet.py` ###
Generate a new random address and put the WIF or encrypted private key on a
wallet. The amount and asset labels are optional and can be left blank.

Usage: 

    python2 genpaperwallet.py -encrypt --amount ZERO --asset USD --design cass mypaperwallet.pdf

### `json2paperwallet.py` ###
Useful helper script in combination with `bts_create_key` from the `utils/` of
the original client.

Usage:

    bitshares/programs/utils/bts_create_key | python2 json2paperwallet.py -encrypt --amount ZERO --asset USD --design cass mympaperwallet.pdf

### `genbulkwallets.py` ###
Automatically generate alot of paperwallets from a .csv file. This tool is
intended for giveaways, i.e. sharedrops. The file `wallet-example.cvs`
contains an example for the input data required for this tool. The columns in
this order are

* Private key in WIF format (no encryption)
* BTS address
* Amount (Text field that is put next to the private key)
* Asset (Logo of the asset)

Usage:

    python2 genbulkwallets.py wallet-example.csv

Example:

    $ python2 paperwallets.py 
    Constructing paper wallets
    Creating Paperwallet for BTS4PuD3QAJGZdF9ynn4Xd9MPYUnRCroK7cF
    Creating Paperwallet for BTS2yzeYXLepsRRMgRKNkr6HSNUwpW2n1C3T
    Creating Paperwallet for BTS51vutXwkjZb1TsJ5paxh38JpCsHV7uuAd
    Creating Paperwallet for BTSJtaUDH2VLTkmynT6V99topWjSxGL4hAzV
    Creating Paperwallet for BTS6kXeyiGTdJMBzoTLpXz3t5gRKDAyCnwrH
    Creating Paperwallet for BTSGVErjYEyUk2wux7fnJWvDmCQxjAPF4y22
    Creating Paperwallet for BTS2mr4wAuBoi3jaSFsm2N8Zzae3hBa3rpmi
    Creating Paperwallet for BTS7jJcGDftS9YxpEd1J8tuakxia5Ugw9ju
    Creating Paperwallet for BTS2RZquTmF3qmnrzfECQGaAeBoy7sMpJiWi
    Done.

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
