#!/usr/bin/env python
import time
import os
import json
import sha3
import signal
import test_node
import subprocess
from pyrpctools import RPC_Client, MAXGAS
from colorama import Style, Fore, init; init()

test_code = {'foobar':{'sqrt.se':'''\
def sqrt(x):
    with guess = ONE:
        guess = avg(guess, fdiv(x, guess))
        guess = avg(guess, fdiv(x, guess))
        guess = avg(guess, fdiv(x, guess))
        guess = avg(guess, fdiv(x, guess))
        guess = avg(guess, fdiv(x, guess))
        guess = avg(guess, fdiv(x, guess))
        guess = avg(guess, fdiv(x, guess))
        guess = avg(guess, fdiv(x, guess))
        guess = avg(guess, fdiv(x, guess))
        return(avg(guess, fdiv(x, guess)))

inset('math_macros.sm')
''',
                       'foo.se':'''\
import sqrt as SQRT

def bar(x):
    s = SQRT.sqrt(x)
    return(fdiv(2*s, s - ONE))

inset('math_macros.sm')
''',
                       'math_macros.sm':'''\
macro ONE: 0x10000000000000000

macro fdiv($a, $b):
    $a*ONE/$b

macro avg($a, $b):
    ($a + $b)/2
'''}}

ONE = 0x10000000000000000

def fdiv(a, b):
    return a*ONE/b

def avg(a, b):
    return (a + b)/2

def sqrt(x):
    guess = ONE
    guess = avg(guess, fdiv(x, guess))
    guess = avg(guess, fdiv(x, guess))
    guess = avg(guess, fdiv(x, guess))
    guess = avg(guess, fdiv(x, guess))
    guess = avg(guess, fdiv(x, guess))
    guess = avg(guess, fdiv(x, guess))
    guess = avg(guess, fdiv(x, guess))
    guess = avg(guess, fdiv(x, guess))
    guess = avg(guess, fdiv(x, guess))
    return(avg(guess, fdiv(x, guess)))

def bar(x):
    s = sqrt(x)
    return(fdiv(2*s, s - ONE))

def make_tree(file_tree):
    top_dir = os.getcwd() # get the current working directory
    for name, data in file_tree.items():
        if type(data) == dict: # make a folder, and write its contents to disk
            os.mkdir(name)
            os.chdir(name)
            make_tree(data)
            os.chdir(top_dir)
        elif type(data) in (str, unicode): #write the text to a file
            with open(name, 'w') as datafile:
                datafile.write(data)

def rm_tree(file_tree):
    top_dir = os.getcwd()
    for name, data in file_tree.items():
        if type(data) == dict:
            os.chdir(name)
            rm_tree(data)
            os.chdir(top_dir)
            os.rmdir(name)
        elif type(data) in (str, unicode):
            os.remove(name)

def start_test_node():
    test_node.LOG = open("test_load_contracts_node.log", 'w')
    test_node.setup_environment()
    test_node.make_address()
    return test_node.start_node()

def test_compile_imports():
    make_tree(test_code)
    node = start_test_node()

    rpc = RPC_Client((test_node.HOST, test_node.PORT), 0)
    coinbase = rpc.eth_coinbase()['result']
    gas_price = int(rpc.eth_gasPrice()['result'], 16)
    balance = 0

    while balance/gas_price < int(MAXGAS, 16):
        balance = int(rpc.eth_getBalance(coinbase)['result'], 16)
        time.sleep(1)

    subprocess.check_call(['python',
                           'load_contracts.py',
                           '-p', '9696',
                           '-b', '2',
                           '-d', 'test_load_contracts.json',
                           '-s', 'foobar'])

    db = json.load(open("test_load_contracts.json"))
    func1 = db['foo']['fullsig'][0]['name']
    prefix = sha3.sha3_256(func1.encode('ascii')).hexdigest()[:8]
    arg = hex(1 << 65)[2:].strip('L').rjust(64, '0')
    r1 = rpc.eth_call(sender=coinbase,
                      to=db['foo']['address'],
                      data=('0x' + prefix + arg),
                      gas=hex(3*10**6))['result']

    r1 = int(r1, 16)
    if r1 > 2**255:
        r1 -= 2**256
    r2 = bar(1 << 65)
    if r1 == r2:
        print 'TEST PASSED'
    else:
        print 'TEST FAILED: <r1 {}> <r2 {}>'.format(r1, r2)
    rm_tree(test_code)
    node.send_signal(signal.SIGINT)
    node.wait()
    
if __name__ == '__main__':
    test_compile_imports()
