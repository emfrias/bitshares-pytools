#!/usr/bin/env python2
import json
import sys
import argparse

try :
    import bitsharestools.address as Address
    import bitsharestools.base58 as b58
    import bitsharestools.bip38 as b38
    import bitsharestools.transactions as Transaction
except ImportError :
    raise ImportError('Module bitsharestools missing')

'''
Meta function to read stuff from QR code
'''
def readtextfromQR():
    try :
        from qrtools import QR
        from codecs import BOM_UTF8
    except ImportError :
        print('Module qrtools missing! No QR-code import possible!')
        raise 
    myCode = QR()
    myCode.decode_webcam()
    key = myCode.data_to_string().strip()
    return key[len(BOM_UTF8):] # fixes zbar!

def ask_for_decryption(privkey_raw) :
    import getpass
    while True :
        try :
            print("The private key is encrypted. A passphrase is required!")
            pw = getpass.getpass('Passphrase: ')
            return b38.bip38_decrypt(privkey_raw,pw)
        except (EOFError, KeyboardInterrupt):
            print
            sys.exit(1)
        except Exception, e:
            print("Error: %s. Try again!" % str(e))
            continue

'''
Ask for the private key, if not manual (copy/pase) then go to QR-codes
'''
def ask_for_privkey() :
    while True :
        try :
            print("1) Type in WIF private key")
            print("2) Use QR scanner")
            choice = raw_input("Select option: ")
            if choice == "1" :
                privkey_raw = raw_input("Please provide private key (WIF): ")
            elif choice == "2" :
                print("Press any key if the green rectangle appears!")
                privkey_raw = readtextfromQR()
            else :
                continue

            if privkey_raw[0] == "6" :
                privkey = ask_for_decryption(privkey_raw)
            elif privkey_raw[0] == "5" :
                privkey = privkey_raw
            else :
                raise Exception("Expecting WIF/BIP38 private key!")

            ''' Verify that the given private key gives access to the cold storage address '''
            address = Address.priv2btsaddr(Address.wif2hex(privkey))
            return str(privkey).strip(), str(address).strip()

        except Exception, e:
            print("Error: %s" % str(e))
            print("Try again!")
            continue
        except (EOFError, KeyboardInterrupt):
            print
            sys.exit(1)
        except :
            print("Error parsing privkey. Try again")
            continue


def main() :
    ''' Ask for the private key '''
    privkey, address = ask_for_privkey()
    print("Private key gives access to address: %s" % ( address) )

if __name__ == '__main__':
    main()
