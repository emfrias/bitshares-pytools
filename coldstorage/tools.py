'''
Verify that the funds the user wants to withdraw are available according to the balance file
'''
def check_availability(balances, want) :
    have = {}
    for b in balances :
        have[ b[1] ] = b[0]
    for b in want.keys() : 
        if b in have.keys() :
            if want[b] > have[b] : 
                raise Exception("You don't have %f %s" %( want[b], b ))
            continue
        else :
            raise Exception("You dont have a balance %d" % b)
''' 
Prepare an array of data used to construct the transaction
'''
def prepare_withdraw( have, want ) :
    s = []
    for w in want.keys() : 
        for h in have :
            if w in h :
                amount     = want[w]
                symbol     = h[1]
                asset_id   = h[2]
                precision  = h[3]
                balance_id = h[4]
                owner      = h[5]
                s.append( [ amount*precision, symbol, asset_id, precision, balance_id, owner ] )
    return s

'''
Add the txfee as BTS
'''
def addfee( w, fee ) :
    fee = float( fee )
    print("Adding tx fee of %f BTS" % fee)
    if "BTS" in w.keys() :
        w["BTS"] += fee
    else :
        w["BTS"] = fee
    return w

'''
Ask user to input the amount of funds he wants to withdraw
'''
def input_transfer_asset_balances() :
    withdraw = {}
    while True :
        i = raw_input("Give amount AND asset [10 BTS]: ")
        try :
            amount,assetname = i.split(" ")
            withdraw[ assetname ] = float(amount)
        except :
            print("Error reading input. Try again! Example: 10 BTS")
            continue

        print("Going to withdraw:")
        for w in withdraw.keys() :
            print("%f %s" %( withdraw[w], w))

        if rpc.query_yes_no( "Want more?" ) :
            continue
        break
    withdrawUnique = {}
    for b in withdraw.keys() :
        if b in withdrawUnique.keys() :
            withdrawUnique[ b ] += withdraw[b]
        else :
            withdrawUnique[ b ] = withdraw[b]
    return withdrawUnique

'''
If not given as parameter, ask the user for the hot wallet address
'''
def ask_for_address() :
    global PREFIX
    while True :
        try :
            address = raw_input("Please type the BTS address(!) of the recipient! (wallet_create_address <account>) [empty for QR scanner]: ")
            if address == "" :
                print("Press any key if the green rectangle appears!")
                address = readtextfromQR()
            b58.btsBase58CheckDecode(address[len(PREFIX):])
            return address
        except (EOFError, KeyboardInterrupt):
            print # end in newline
            sys.exit(1)
        except :
            print("Error parsing address. Try again!")
            continue

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

'''
Read the balance file given from the online tool and return the available data
'''
def readBalanceFile(filename) :
    balances = [  ]
    with open( filename, "rb" ) as fp :
        print("Available funds in the cold storage address:")
        for l in fp.readlines() :
            try :
                amount,symbol,assetid,precision,balanceid,owner = l.split(";") 
                balances.append([ float(amount.strip()), symbol.strip(), int(assetid.strip()), int(precision.strip()), balanceid.strip(), owner.strip()])
                print( " - %f %s" %( float(amount.strip()), symbol.strip() ) )
            except :
                print("Syntax error in file. Try again!")
                raise
    return balances

'''
Get available funds from bitshares rpc
'''
def get_available_balances(rpc, address):
    balances = []
    for b in rpc.blockchain_list_address_balances(address)["result"] :
        asset_id = b[1]["condition"]["asset_id"]
        asset    = rpc.blockchain_get_asset(asset_id)["result"]
        balances.append( {
                "balanceid" : b[0],
                "balance"   : (b[1]["balance"])/float(asset["precision"]),
                "symbol"    : asset["symbol"],
                "asset_id"  : asset["id"],
                "precision" : asset["precision"],
                "owner"     : b[1]["condition"]["data"]["owner"]
            })
    return balances

'''
Decrypt BIP38 encrypted wif
'''
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
def ask_for_privkey(address) :
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
            addressraw = Address.priv2btsaddr(Address.wif2hex(privkey))
            print("This private key gives access to funds in address %s" % addressraw)
            if str(address).strip() == str(addressraw).strip() :
                return str(privkey).strip()
            else :
                print("The private key is wrong! It gives access to %s but access to %s is required to sign this tx" % (addressraw, address))
                raise

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
