import datetime
import json
import struct
import binascii
import hashlib
import math
import genbtskey as btskey
import ecdsa
import sys
from pprint import pprint
import time
from copy import copy

def varint(n):
    if n < 0xfd:
        return struct.pack('<B', n)
    elif n < 0xffff:
        return struct.pack('<cH', '\xfd', n)
    elif n < 0xffffffff:
        return struct.pack('<cL', '\xfe', n)
    else:
        return struct.pack('<cQ', '\xff', n)

def variable_buffer( s ) :
    return varint(len(s)) + s

bts_operations = {}
bts_operations["null_op_type"] = 0

# balance operations
bts_operations["withdraw_op_type"]=1
bts_operations["deposit_op_type"]=2

# account operations
bts_operations["register_account_op_type"]=3
bts_operations["update_account_op_type"]=4
bts_operations["withdraw_pay_op_type"]=5

# asset operations"
bts_operations["create_asset_op_type"]=6
bts_operations["update_asset_op_type"]=7
bts_operations["issue_asset_op_type"]=8

# delegate operations"
bts_operations["fire_delegate_op_type"]=9

# proposal operations"
bts_operations["submit_proposal_op_type"]=10
bts_operations["vote_proposal_op_type"]=11

# market operations"
bts_operations["bid_op_type"]=12
bts_operations["ask_op_type"]=13
bts_operations["short_op_type"]=14
bts_operations["cover_op_type"]=15
bts_operations["add_collateral_op_type"]=16
bts_operations["remove_collateral_op_type"]=17
bts_operations["define_delegate_slate_op_type"]=18
bts_operations["update_feed_op_type"]=19
bts_operations["burn_op_type"]=21
bts_operations["link_account_op_type"]=22
bts_operations["withdraw_all_op_type"]=23
bts_operations["release_escrow_op_type"]=24

bts_withdraw = {}
bts_withdraw["withdraw_null_type"]=0
bts_withdraw["withdraw_signature_type"]=1
bts_withdraw["withdraw_multi_sig_type"]=2
bts_withdraw["withdraw_password_type"]=3
bts_withdraw["withdraw_option_type"]=4
bts_withdraw["withdraw_escrow_type"]=5
bts_withdraw["withdraw_vesting_type"]=6

#memo = types.memo = []
#memo[0]="from_memo"
#memo[1]="to_memo"

chainid        = "75c11a81b7670bbaa721cc603eadb2313756f94a3bcbb9928e9101432701ac5f"
PREFIX         = "BTS"

class WithdrawSignatureType(object) :
    def __init__(self, receiveAddress, otk=None, memo_data=None) :
        self.owner = receiveAddress
#        if otk and memo_data:
#            self.memo["one_time_key"]        = btskey.btsbase58CheckDecode(self.otk[len(PREFIX):])
#            self.memo["encrypted_memo_data"] = memo_data
    def towire(self) :
        wire  = struct.pack("<20s",btskey.btsbase58CheckDecode(self.owner[len(PREFIX):]))
#        if self.has_key( memo ) :
#            wire += struct.pack("<B", 0x01)
#            wire += struct.pack("<33s",self.memo["one_time_key"])
#            wire += variable_buffer( self.memo["encrypted_memo_data"] )
#        else :
        wire += struct.pack("<B", 0x00)   ## optional True/False
        return wire
    def tojson(self) :
        return vars(self)

class WithdrawCondition(object) :
    def __init__( self, asset_id, slate_id, condition_type, condition ) :
        self.asset_id = asset_id
        self.slate_id = slate_id
        self.type = condition_type
        self.data = condition
    def towire(self) :
        wire  = varint(self.asset_id)
        wire += struct.pack("<Q",self.slate_id) 
        wire += struct.pack("<B",bts_withdraw[self.type]) 
        wire += variable_buffer(self.data.towire())
        return wire
    def tojson(self) :
        d = vars(copy(self))
        d["data"] = self.data.tojson()
        return d

class Deposit(object) :
    def __init__( self, amount, condition ) :
        self.amount = int(amount)
        self.condition = condition
    def towire(self) :
        wire = struct.pack("<Q",self.amount)
        wire += self.condition.towire()
        return wire
    def tojson(self) :
        d = vars(copy(self))
        d["condition"] = self.condition.tojson()
        return d

class Withdraw(object) :
    def __init__( self, balance_id, amount, claimdata="") :
        self.balance_id = balance_id
        self.amount = int(amount)
        self.claim_input_data = claimdata
    def towire(self) :
        wire  = struct.pack("<20s",btskey.btsbase58CheckDecode(self.balance_id[len(PREFIX):]))
        wire += struct.pack("<Q",self.amount)
        wire += variable_buffer(self.claim_input_data)
        return wire
    def tojson(self) :
        return vars(self)

class Operation(object) :
    def __init__( self, optype, operation ) :
        self.type = optype
        self.data = operation
    def towire(self) :
        wire  = struct.pack("<B",bts_operations[self.type])  # deposit_op_type = 2;
        wire += variable_buffer(self.data.towire())
        return wire
    def tojson(self) :
        d = vars(copy(self))
        d["data"] = self.data.tojson()
        return d

class Transaction(object) :
    def __init__( self, timeoutsecs, slate_id, operations ) :
        self.expiration = int(time.time()) + timeoutsecs
        self.slate_id = slate_id
        self.operations = operations
    def towire(self) :
        wire  = struct.pack("<I",self.expiration)  ## expiration time
        wire += struct.pack("<B",self.slate_id)         ## true/false slate_id
        wire += varint(len(self.operations))
        for op in self.operations :
            wire += op.towire()
        return wire
    def tojson(self) :
        d = vars(copy(self))
        d["expiration"] = datetime.datetime.fromtimestamp(int(d["expiration"])).strftime('%Y-%m-%dT%H:%M:%S')
        d["operations"] = []
        for op in self.operations :
            d["operations"].append(op.tojson())
        return d

class SignedTransaction(object) : 
    def derSigToHexSig(self, s):
        s, junk = ecdsa.der.remove_sequence(s.decode('hex'))
        if junk != '':
            print('JUNK', junk.encode('hex'))
        assert(junk == '')
        x, s = ecdsa.der.remove_integer(s)
        y, s = ecdsa.der.remove_integer(s)
        return '%064x%064x' % (x, y)

    def recoverPubkeyParameter(self, digest, signature, pubkey) :
        for i in xrange(0,4) :
            p = self.signature_to_public_key(digest, signature, i)
            if p.to_string() == pubkey.to_string() :
                return i
        return None

    def signature_to_public_key(self, digest, signature, i):
        # See http://www.secg.org/download/aid-780/sec1-v2.pdf section 4.1.6 primarily
        curve = ecdsa.SECP256k1.curve
        G     = ecdsa.SECP256k1.generator
        order = ecdsa.SECP256k1.order
        isYOdd      = i % 2
        isSecondKey = i // 2
        yp = 0 if (isYOdd) == 0 else 1
        r, s = ecdsa.util.sigdecode_string(signature, order)
        # 1.1
        x = r + isSecondKey * order
        # 1.3. This actually calculates for either effectively 02||X or 03||X depending on 'k' instead of always for 02||X as specified.
        # This substitutes for the lack of reversing R later on. -R actually is defined to be just flipping the y-coordinate in the elliptic curve.
        alpha = ((x * x * x) + (curve.a() * x) + curve.b()) % curve.p()
        beta = ecdsa.numbertheory.square_root_mod_prime(alpha, curve.p())
        if (beta - yp) % 2 == 0:
            y = beta
        else:
            y = curve.p() - beta
        # 1.4 Constructor of Point is supposed to check if nR is at infinity. 
        R = ecdsa.ellipticcurve.Point(curve, x, y, order)
        # 1.5 Compute e
        e = ecdsa.util.string_to_number(digest)
        # 1.6 Compute Q = r^-1(sR - eG)
        Q = ecdsa.numbertheory.inverse_mod(r, order) * (s * R + (-e % order) * G)
        # Not strictly necessary, but let's verify the message for paranoia's sake.
        #if ecdsa.VerifyingKey.from_public_point(Q, curve=ecdsa.SECP256k1).verify_digest(signature, digest, sigdecode=ecdsa.util.sigdecode_string) != True:
        #    return None
        #return Q
        return ecdsa.VerifyingKey.from_public_point(Q, curve=ecdsa.SECP256k1)

    def __init__( self, transaction, privatekeys ) :
        self.transaction = transaction
        self.privkeys = privatekeys
        self.chainid  = chainid
        self.message  = str(transaction.towire()) + str(binascii.unhexlify(chainid))
        self.digest   = hashlib.sha256( self.message ).digest()
        self.signatures = self.signtx()

    def signtx(self) :
        sigs = []
        for wif in self.privkeys :
            p         = btskey.wifKeyToPrivateKey(wif).decode('hex')
            sk        = ecdsa.SigningKey.from_string(p, curve=ecdsa.SECP256k1)
            sigder    = sk.sign_deterministic(self.message, hashfunc=hashlib.sha256,sigencode=ecdsa.util.sigencode_der)
            hexSig    = self.derSigToHexSig(binascii.hexlify(sigder))  # DER decode
            signature = binascii.unhexlify(hexSig)
            ## Recovery parameter
            r, s      = ecdsa.util.sigdecode_string(signature, ecdsa.SECP256k1.order)
            assert sk.get_verifying_key().verify(signature, self.message, hashfunc=hashlib.sha256) ## verify valid pubkey
            assert ecdsa.curves.orderlen( r ) == 32 ## Verify length or r and s
            assert ecdsa.curves.orderlen( s ) == 32 ## Verify length or r and s
            i = self.recoverPubkeyParameter(self.digest, signature, sk.get_verifying_key())
            i += 4 #compressed
            i += 27 #compact
            sigs.append(struct.pack("<B",i) + signature)
        return sigs

    def towire(self) :
        wire = self.transaction.towire()
        wire += varint( len( self.signatures ) )                # number of signatures
        for s in self.signatures :
            wire += s
        return wire

    def tojson(self) :
        d = self.transaction.tojson()
        d["signatures"] = []
        for s in self.signatures :
            d["signatures"].append(binascii.hexlify(s))
        return d
