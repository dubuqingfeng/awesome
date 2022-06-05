#!/usr/bin/env python
#
# Copyright 2014 Corgan Labs
# See LICENSE.txt for distribution terms
#

import os
import hmac
import hashlib
import ecdsa
import struct

from hashlib import sha256
from ecdsa.curves import SECP256k1
from ecdsa.ecdsa import int_to_string, string_to_int
from ecdsa.numbertheory import square_root_mod_prime as sqrt_mod

MIN_ENTROPY_LEN = 128        # bits
BIP32_HARDEN    = 0x80000000 # choose from hardened set of child keys
CURVE_GEN       = ecdsa.ecdsa.generator_secp256k1
CURVE_ORDER     = CURVE_GEN.order()
FIELD_ORDER     = SECP256k1.curve.p()
INFINITY        = ecdsa.ellipticcurve.INFINITY
EX_MAIN_PRIVATE = bytes.fromhex('0488ade4') # Version string for mainnet extended private keys
EX_MAIN_PUBLIC  = bytes.fromhex('0488b21e') # Version string for mainnet extended public keys

# base58 encoding and decoding functions
from hashlib import sha256
import unittest
import re

__base58_alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__base58_alphabet_bytes = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__base58_radix = len(__base58_alphabet)


def __string_to_int(data):
    "Convert string of bytes Python integer, MSB"
    val = 0
   
    # Python 2.x compatibility
    if type(data) == str:
        data = bytearray(data)

    for (i, c) in enumerate(data[::-1]):
        val += (256**i)*c
    return val


def encode(data):
    "Encode bytes into Bitcoin base58 string"
    enc = ''
    val = __string_to_int(data)
    while val >= __base58_radix:
        val, mod = divmod(val, __base58_radix)
        enc = __base58_alphabet[mod] + enc
    if val:
        enc = __base58_alphabet[val] + enc

    # Pad for leading zeroes
    n = len(data)-len(data.lstrip(b'\0'))
    return __base58_alphabet[0]*n + enc


def check_encode(raw):
    "Encode raw bytes into Bitcoin base58 string with checksum"
    chk = sha256(sha256(raw).digest()).digest()[:4]
    return encode(raw+chk)


def decode(data):
    "Decode Bitcoin base58 format string to bytes"
    # Python 2.x compatability
    x00 = re.findall(r"^[1]+", data)
    x00 = len(x00[0]) if x00 else 0
    
    if bytes != str:
        data = bytes(data, 'ascii')
    
    val = 0
    for (i, c) in enumerate(data[::-1]):
        val += __base58_alphabet_bytes.find(c) * (__base58_radix**i)

    dec = bytearray()
    while val >= 256:
        val, mod = divmod(val, 256)
        dec.append(mod)
    if val:
        dec.append(val)

    return b"\x00"*x00 + bytes(dec[::-1])


def check_decode(enc, need_prefix = False):
    "Decode bytes from Bitcoin base58 string and test checksum"
    dec = decode(enc)
    raw, chk = dec[:-4], dec[-4:]
    if chk != sha256(sha256(raw).digest()).digest()[:4]:
        raise ValueError("base58 decoding checksum error")
    elif not need_prefix:
        return raw[1:]
    return raw


class BIP32Key(object):

    # Static initializers to create from entropy or external formats
    #
    @staticmethod
    def fromEntropy(entropy, public=False):
        "Create a BIP32Key using supplied entropy >= MIN_ENTROPY_LEN"
        if entropy == None:
            entropy = os.urandom(MIN_ENTROPY_LEN/8) # Python doesn't have os.random()
        if not len(entropy) >= MIN_ENTROPY_LEN/8:
            raise ValueError("Initial entropy %i must be at least %i bits" %
                                (len(entropy), MIN_ENTROPY_LEN))
        I = hmac.new(b"Bitcoin seed", entropy, hashlib.sha512).digest()
        Il, Ir = I[:32], I[32:]
        # FIXME test Il for 0 or less than SECP256k1 prime field order
        key = BIP32Key(secret=Il, chain=Ir, depth=0, index=0, fpr=b'\0\0\0\0', public=False)
        if public:
            key.SetPublic()
        return key

    @staticmethod
    def fromExtendedKey(xkey, public=False):
        """
        Create a BIP32Key by importing from extended private or public key string
        If public is True, return a public-only key regardless of input type.
        """
        # Sanity checks
        raw = check_decode(xkey)
        if len(raw) != 78:
            raise ValueError("extended key format wrong length")

        # Verify address version/type
        version = raw[:4]
        if version == EX_MAIN_PRIVATE:
            keytype = 'xprv'
        elif version == EX_MAIN_PUBLIC:
            keytype = 'xpub'
        else:
            raise ValueError("unknown extended key version")

        # Extract remaining fields
        depth = ord(raw[4])
        fpr = raw[5:9]
        child = struct.unpack(">L", raw[9:13])[0]
        chain = raw[13:45]
        secret = raw[45:78]

        # Extract private key or public key point
        if keytype == 'xprv':
            secret = secret[1:]
        else:
            # Recover public curve point from compressed key
            lsb = ord(secret[0]) & 1
            x = string_to_int(secret[1:])
            ys = (x**3+7) % FIELD_ORDER # y^2 = x^3 + 7 mod p
            y = sqrt_mod(ys, FIELD_ORDER)
            if y & 1 != lsb:
                y = FIELD_ORDER-y
            point = ecdsa.ellipticcurve.Point(SECP256k1.curve, x, y)
            secret = ecdsa.VerifyingKey.from_public_point(point, curve=SECP256k1)

        is_pubkey = (keytype == 'xpub')
        key = BIP32Key(secret=secret, chain=chain, depth=depth, index=child, fpr=fpr, public=is_pubkey)
        if not is_pubkey and public:
            key = key.SetPublic()
        return key


    # Normal class initializer
    def __init__(self, secret, chain, depth, index, fpr, public=False):
        """
        Create a public or private BIP32Key using key material and chain code.
        secret   This is the source material to generate the keypair, either a
                 32-byte string representation of a private key, or the ECDSA
                 library object representing a public key.
        chain    This is a 32-byte string representation of the chain code
        depth    Child depth; parent increments its own by one when assigning this
        index    Child index
        fpr      Parent fingerprint
        public   If true, this keypair will only contain a public key and can only create
                 a public key chain.
        """

        self.public = public
        if public is False:
            self.k = ecdsa.SigningKey.from_string(secret, curve=SECP256k1)
            self.K = self.k.get_verifying_key()
        else:
            self.k = None
            self.K = secret

        self.C = chain
        self.depth = depth
        self.index = index
        self.parent_fpr = fpr


    # Internal methods not intended to be called externally
    #
    def hmac(self, data):
        """
        Calculate the HMAC-SHA512 of input data using the chain code as key.
        Returns a tuple of the left and right halves of the HMAC
        """
        I = hmac.new(self.C, data, hashlib.sha512).digest()
        return (I[:32], I[32:])


    def CKDpriv(self, i):
        """
        Create a child key of index 'i'.
        If the most significant bit of 'i' is set, then select from the
        hardened key set, otherwise, select a regular child key.
        Returns a BIP32Key constructed with the child key parameters,
        or None if i index would result in an invalid key.
        """
        # Index as bytes, BE
        i_str = struct.pack(">L", i)

        # Data to HMAC
        if i & BIP32_HARDEN:
            data = b'\0' + self.k.to_string() + i_str
        else:
            data = self.PublicKey() + i_str

        # Get HMAC of data
        (Il, Ir) = self.hmac(data)

        # Construct new key material from Il and current private key
        Il_int = string_to_int(Il)
        if Il_int > CURVE_ORDER:
            return None
        pvt_int = string_to_int(self.k.to_string())
        k_int = (Il_int + pvt_int) % CURVE_ORDER
        if (k_int == 0):
            return None
        secret = int_to_string(k_int)

        # Construct and return a new BIP32Key
        return BIP32Key(secret=secret, chain=Ir, depth=self.depth+1, index=i, fpr=self.Fingerprint(), public=False)


    def CKDpub(self, i):
        """
        Create a publicly derived child key of index 'i'.
        If the most significant bit of 'i' is set, this is
        an error.
        Returns a BIP32Key constructed with the child key parameters,
        or None if index would result in invalid key.
        """

        if i & BIP32_HARDEN:
            raise Exception("Cannot create a hardened child key using public child derivation")

        # Data to HMAC.  Same as CKDpriv() for public child key.
        data = self.PublicKey() + struct.pack(">L", i)

        # Get HMAC of data
        (Il, Ir) = self.hmac(data)

        # Construct curve point Il*G+K
        Il_int = string_to_int(Il)
        if Il_int >= CURVE_ORDER:
            return None
        point = Il_int*CURVE_GEN + self.K.pubkey.point
        if point == INFINITY:
            return None

        # Retrieve public key based on curve point
        K_i = ecdsa.VerifyingKey.from_public_point(point, curve=SECP256k1)

        # Construct and return a new BIP32Key
        return BIP32Key(secret=K_i, chain=Ir, depth=self.depth, index=i, fpr=self.Fingerprint(), public=True)


    # Public methods
    #
    def ChildKey(self, i):
        """
        Create and return a child key of this one at index 'i'.
        The index 'i' should be summed with BIP32_HARDEN to indicate
        to use the private derivation algorithm.
        """
        if self.public is False:
            return self.CKDpriv(i)
        else:
            return self.CKDpub(i)


    def SetPublic(self):
        "Convert a private BIP32Key into a public one"
        self.k = None
        self.public = True


    def PrivateKey(self):
        "Return private key as string"
        if self.public:
            raise Exception("Publicly derived deterministic keys have no private half")
        else:
            return self.k.to_string()


    def PublicKey(self):
        "Return compressed public key encoding"
        if self.K.pubkey.point.y() & 1:
            ck = b'\3'+int_to_string(self.K.pubkey.point.x())
        else:
            ck = b'\2'+int_to_string(self.K.pubkey.point.x())
        return ck


    def ChainCode(self):
        "Return chain code as string"
        return self.C


    def Identifier(self):
        "Return key identifier as string"
        cK = self.PublicKey()
        return hashlib.new('ripemd160', sha256(cK).digest()).digest()


    def Fingerprint(self):
        "Return key fingerprint as string"
        return self.Identifier()[:4]


    def Address(self):
        "Return compressed public key address"
        vh160 = b'\x00'+self.Identifier()
        return check_encode(vh160)


    def WalletImportFormat(self):
        "Returns private key encoded for wallet import"
        if self.public:
            raise Exception("Publicly derived deterministic keys have no private half")
        raw = b'\x80' + self.k.to_string() + b'\x01' # Always compressed
        return check_encode(raw)


    def ExtendedKey(self, private=True, encoded=True):
        "Return extended private or public key as string, optionally Base58 encoded"
        if self.public is True and private is True:
            raise Exception("Cannot export an extended private key from a public-only deterministic key")
        version = EX_MAIN_PRIVATE if private else EX_MAIN_PUBLIC
        depth = self.depth.to_bytes(2, byteorder='big')
        fpr = self.parent_fpr
        child = struct.pack('>L', self.index)
        chain = self.C
        if self.public is True or private is False:
            data = self.PublicKey()
        else:
            data = b'\x00' + self.PrivateKey()

        raw = version+depth+fpr+child+chain+data
        if not encoded:
            return raw
        else:
            return check_encode(raw)

    # Debugging methods
    #
    def dump(self):
        "Dump key fields mimicking the BIP0032 test vector format"
        print("   * Identifier")
        print("     * (hex):      ", self.Identifier().hex())
        print("     * (fpr):      ", self.Fingerprint().hex())
        print("     * (main addr):", self.Address())
        if self.public is False:
            print("   * Secret key")
            print("     * (hex):      ", self.PrivateKey().hex())
            print("     * (wif):      ", self.WalletImportFormat())
        print("   * Public key")
        print("     * (hex):      ", self.PublicKey().hex())
        print("   * Chain code")
        print("     * (hex):      ", self.C.hex())
        print("   * Serialized")
        print("     * (pub hex):  ", self.ExtendedKey(private=False, encoded=False).hex())
        print("     * (prv hex):  ", self.ExtendedKey(private=True, encoded=False).hex())
        print("     * (pub b58):  ", self.ExtendedKey(private=False, encoded=True))
        print("     * (prv b58):  ", self.ExtendedKey(private=True, encoded=True))


if __name__ == "__main__":
    import sys

    # BIP0032 Test vector 1
    entropy=bytearray.fromhex('000102030405060708090A0B0C0D0E0F')
    # entropy='000102030405060708090A0B0C0D0E0F'.decode('hex')
    m = BIP32Key.fromEntropy(entropy)
    print("Test vector 1:")
    print("Master (hex):", entropy.hex())
    print("* [Chain m]")
    m.dump()

    print("* [Chain m/0h]")
    m = m.ChildKey(0+BIP32_HARDEN)
    m.dump()

    print("* [Chain m/0h/1]")
    m = m.ChildKey(1)
    m.dump()

    print("* [Chain m/0h/1/2h]")
    m = m.ChildKey(2+BIP32_HARDEN)
    m.dump()

    print("* [Chain m/0h/1/2h/2]")
    m = m.ChildKey(2)
    m.dump()

    print("* [Chain m/0h/1/2h/2/1000000000]")
    m = m.ChildKey(1000000000)
    m.dump()

    # BIP0032 Test vector 2
    entropy = bytes.fromhex('fffcf9f6f3f0edeae7e4e1dedbd8d5d2cfccc9c6c3c0bdbab7b4b1aeaba8a5a29f9c999693908d8a8784817e7b7875726f6c696663605d5a5754514e4b484542')
    # entropy = 'fffcf9f6f3f0edeae7e4e1dedbd8d5d2cfccc9c6c3c0bdbab7b4b1aeaba8a5a29f9c999693908d8a8784817e7b7875726f6c696663605d5a5754514e4b484542'.decode('hex')
    m = BIP32Key.fromEntropy(entropy)
    print("Test vector 2:")
    print("Master (hex):", entropy.hex())
    print("* [Chain m]")
    m.dump()

    print("* [Chain m/0]")
    m = m.ChildKey(0)
    m.dump()

    print("* [Chain m/0/2147483647h]")
    m = m.ChildKey(2147483647+BIP32_HARDEN)
    m.dump()

    print("* [Chain m/0/2147483647h/1]")
    m = m.ChildKey(1)
    m.dump()

    print("* [Chain m/0/2147483647h/1/2147483646h]")
    m = m.ChildKey(2147483646+BIP32_HARDEN)
    m.dump()

    print("* [Chain m/0/2147483647h/1/2147483646h/2]")
    m = m.ChildKey(2)
    m.dump()