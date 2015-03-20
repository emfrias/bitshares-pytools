## What's this ##
These tools generate (encrypted) paperwallets in SVG.

## Requirements ##
The following python libaries are required:
* csv
* qrcode
* lxml
For BIP38 encrypted paperwallets:
* python2-pybitcointools
* python2-scrypt

## Features ##
The following images and text boxes are individually replaced:
* QR code for address
* QR code for private key
* Address as text
* Amount
* Asset logo

## Example ##

### `paperwallets.py` ###
Automatically generate alot of paperwallets from a .csv file. This tool is
intended for giveaways, i.e. sharedrops.
The file `wallet-example.cvs` contains an example for the input data required
for this tool. The columns in this order are

* Private key in WIF format (no encryption)
* BTS address
* Amount (Text field that is put next to the private key)
* Asset (Logo of the asset)

### `genpaperwallet.py` ###
Generate a new random address and put the WIF or encrypted private key on a
wallet. The amount and asset labels are optional and can be left blank.

Usage: 

    python2 genpaperwallet.py -encrypt --amount ZERO --asset USD --design cass mympaperwallet.svg

### `json2paperwallet.py` ###
Useful helper script in combination with `bts_create_key` from the `utils/` of
the original client.

Usage:

    bitshares/programs/utils/bts_create_key | python2 json2paperwallet.py -encrypt --amount ZERO --asset USD --design cass mympaperwallet.svg

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
