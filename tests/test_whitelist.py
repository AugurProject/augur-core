from warnings import simplefilter; simplefilter('ignore')
from pyrpctools import RPC_Client, MAXGAS
import test_node
import serpent
import sha3
import json
import os

def test_whitelist():
    node = test_node.TestNode()
    rpc = RPC_Client((node.rpchost, node.rpcport), 0)
    whitelist_path = os.path.realpath('../src/data and api/reporting.se.whitelist')
    code = serpent.compile(whitelist_path).encode('hex')
    fullsig = json.loads(serpent.mk_fullsig(whitelist_path))
    my_address = rpc.eth_coinbase()['result']
    
    print Style.BRIGHT + 'Mining coins...' + Style.RESET_ALL
    while balance/gas_price < int(MAXGAS, 16):
        balance = int(rpc.eth_getBalance(my_address)['result'], 16)
        time.sleep(1)

    txhash = rpc.eth_sendTransaction(sender=my_address,
                                     data=('0x'+code),
                                     gas=MAXGAS)['result']
    while True:
        receipt = rpc.eth_getTransactionReceipt(txhash)['result']
        if receipt is not None:
            check = RPC.eth_getCode(receipt["contractAddress"])['result']
            if check != '0x' and check[2:] in code:
                 contract_address = receipt["contractAddress"]
                 break

    contract = Contract(contract_address, my_address, fullsig, rpc)


    

