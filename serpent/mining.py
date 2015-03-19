# sudo pip install struct, hashlib, sha3
import struct, hashlib
from sha3 import sha3_256
class Hash:
    def __init__(self, nonce):
        self.nonce = nonce

    def hash(self, data, difficulty, steps=1000):
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
            target = 2 ** 256 / difficulty
            rlp_Hn = data
            for nonce in range(self.nonce, self.nonce + steps):
                nonce_bin = nonce_bin_prefix + struct.pack('>q', nonce)
                # BE(SHA3(SHA3(RLP(Hn)) o n))
                h = self.sha3((self.sha3(rlp_Hn) + nonce_bin))
                #log.debug('nonce found', nonce=nonce, hash=(h.encode('hex') or '0'))
                l256 = self.big_endian_to_int(h)
                if l256 < target:
                    return nonce_bin
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

    # PoW verification
    def check__pow(self, metadata, nonce):
        assert len(nonce) == 32
        #difficulty = branch.difficulty
        difficulty = 2
        h = self.sha3(self.sha3(metadata) + nonce)
        if(market+outcome+branch+amount != metadata):
            return(0)
        return self.big_endian_to_int(h) < 2 ** 256 / difficulty