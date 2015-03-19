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
The file `wallet-example.cvs` contains an example for the input data required
for this tool. The columns in this order are

* Private key in WIF format
* BTS address
* Amount
* Asset
