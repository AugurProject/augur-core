from test_suite import *
from hashlib import sha3
from bitcoin import encode



def make_id(description, *ints):
    return sha3(''.join(encode(i,256).rjust(32,'\x00')for i in ints)+description).digest()
