from ethereum import tester as t
from load_contract import GethRPC

def pyeth_test():
    s = t.state()
    c = s.abi_contract('whitelist.se')
    c_addr = '0x' + c.address.encode('hex')
    my_addr = '0x' + t.a0.encode('hex')
    double_code = '''\
extern whitelist.se: [addAddress:ii:s, check:i:i, checkaddr:ii:i, replaceAddress:iii:s]
data whitelist

def init():
    self.whitelist = {}

def double(x):
    if(!self.whitelist.check(msg.sender)):
        return(-1)
    else:
        return(x*2)'''.format(c_addr)

    d = s.abi_contract(double_code)
    d_addr = '0x' + d.address.encode('hex')
    
    weird_code = '''\
extern doubler: [double:i:i]
data doubler

def init():
    self.doubler = {}

def func():
    return([self.doubler.double(msg.sender), msg.sender]:arr)'''.format(d_addr)

    def int_(x):
        return int(x, 16)

    e = s.abi_contract(weird_code)
    e_addr = e.address.encode('hex')

    print d.double(4)
    print c.addAddress(int_(d_addr), int_(my_addr))
    print c.addAddress(int_(d_addr), int_(e_addr))
    print d.double(4)
    print d.double(4, sender=t.k1)
    print e.func()
    print e.func(sender=t.k1)

def gethRPC_test():
    
