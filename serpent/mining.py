# sudo pip install struct, hashlib, sha3, pybitcointools
import struct, hashlib
from sha3 import sha3_256
from bitcoin import encode, decode
class Hash:
    # start nonce
    def __init__(self, nonce):
        self.nonce = nonce

    def hash(self, branch, market, outcome, amount, difficulty, steps=1000):
            """
            It is formally defined as PoW: PoW(H, n) = BE(SHA3(SHA3(RLP(Hn)) o n))
            where:
            RLP(Hn) is the concatenation of buy shares data
            SHA3 is the SHA3 hash function accepting an arbitrary length series of
                bytes and evaluating to a series of 32 bytes (i.e. 256-bit);
            n is the nonce, a series of 32 bytes;
            o is the series concatenation operator;
            BE(X) evaluates to the value equal to X when interpreted as a
                big-endian-encoded integer.
            """
            #difficulty = branch.difficulty
            nonce_bin_prefix = '\x00' * (32 - len(struct.pack('>q', 0)))
            target = 2 ** 254 / difficulty
            rlp_Hn = encode(branch, 256, 32) + encode(market, 256, 32) + encode(outcome, 256, 32) + encode(amount, 256, 32)
            for nonce in range(self.nonce, self.nonce + steps):
                nonce_bin = nonce_bin_prefix + struct.pack('>q', nonce)
                # BE(SHA3(SHA3(RLP(Hn)) o n))
                h = self.sha3((self.sha3(rlp_Hn) + nonce_bin))
                #log.debug('nonce found', nonce=nonce, hash=(h.encode('hex') or '0'))
                l256 = self.big_endian_to_int(h)
                if l256 < target:
                    return decode(nonce_bin, 256)
            self.nonce = nonce
            return False

    @staticmethod
    def sha3(seed):
        return sha3_256(seed).digest()

    @staticmethod
    def big_endian_to_int(string):
        '''convert a big endian binary string to integer'''
        # '' is a special case, treated same as 0
        s = string.encode('hex') or '0'
        return long(s, 16) 

    # PoW verification (done in ethereum)
    def check__pow(self, branch, market, outcome, amount, nonce):
        assert len(nonce) == 32
        #difficulty = branch.difficulty
        difficulty = 10000
        metadata = encode(branch, 256, 32) + encode(market, 256, 32) + encode(outcome, 256, 32) + encode(amount, 256, 32)
        h = self.sha3(self.sha3(metadata) + nonce)
        return self.big_endian_to_int(h) < 2 ** 254 / difficulty

#base 256, 32 bytes each (<= 256)
#encode(val, base, minlen=0)
#decode(string, base)