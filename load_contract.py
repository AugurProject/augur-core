import serpent
from pyrpctools import RPC_Client, DB
from collection import defaultdict
import os
import sys
import json
from load_contracts import get_fullname, broadcast_code

RPC = RPC_Client(default='GETH')
COINBASE = RPC.eth_coinbase()['result']

def build_dependencies():
    # Assumes all code is in src
    deps = defaultdict(list)
    for d, s, fs in os.walk('src'):
        for f in fs:
            for line in open(os.path.join(d, f)):
                if line.startwith('import'):
                    name = line.split(' ')[1]
                    deps[name].append(f[:-3])
    return deps

def compile(fullname, deps):
    new_code = []
    for line in open(fullname):
        line = line.rstrip()
        if line.startswith('import'):
            line = line.split(' ')
            name, sub = line[1], line[3]
            info = json.loads(DB[name])
            new_code.append(info['sig'])
            new_code.append(sub + ' = ' + info['address'])
        else:
            new_code.append(line)
    new_code = '\n'.join(new_code)
    evm = '0x' + serpent.compile(new_code).encode('hex')
    new_address = broadcast_code(evm)
    short_name = os.path.split(fullname)[-1][:-3]
    new_sig = serpent.mk_signature(new_code).replace('main', short_name, 1)
    fullsig = serpent.mk_full_signature(new_code)
    new_info = {'address':new_address, 'sig':new_sig, 'fullsig':fullsig}
    DB[short_name] = json.dumps(new_info)
    if short_name in deps:
        for dep in deps[short_name]:
            dep_fullname = get_full_name(dep)
            compile(dep_fullname, deps)

def main(contract_path):
    deps = build_dependencies()
    compile(contract_path, deps)

if __name__ == '__main__':
    main(sys.argv[1])
