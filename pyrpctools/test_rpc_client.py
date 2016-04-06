from .rpc_client import RPC_Client

def main():
    rpc = RPC_Client()
    rpc.eth_coinbase()
    rpc.net_version()
    result = rpc.web3_sha3('0x' + 'lol'.encode('hex'))['result']
    assert result == '0xf172873c63909462ac4de545471fd3ad3e9eeadeec4608b92d16ce6b500704cc'

if __name__ == '__main__':
    main()
