FROM ethereum/client-go:latest
COPY genesis.json /app/genesis.json
RUN echo "p" > /app/password.txt
RUN geth makedag 0 /app/.ethash

WORKDIR /
COPY start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT /start.sh

# TODO: Use empty password and create an account with a well-known address instead of the one used now, which is unknown.
# For example, the private key below is created with the empty seed and has no password.  The private keys are stored in the keystore directory: https://github.com/ethereum/go-ethereum/wiki/Managing-your-accounts.
# {
#     "id": "e1042fa7-e661-aeb8-ca86-6b9999adc120",
#     "version": 3,
#     "crypto": {
#         "cipher": "aes-128-ctr",
#         "cipherparams": {
#             "iv": "50f44a53e4e11a424074063200b2e333"
#         },
#         "ciphertext": "190abdf9a8e4135defcd3f890a574b178f24a25fbc46f0daab3ffbb83c83a59d",
#         "kdf": "pbkdf2",
#         "kdfparams": {
#             "c": 10240,
#             "dklen": 32,
#             "prf": "hmac-sha256",
#             "salt": "90a1e58cfa95479588cf754dbad73f8019d2469303dd69028e8d7a2f27bf8d82"
#         },
#         "mac": "27a556b61e874e7f41376b4b01930caf36cee1977722f441fb73ad8cb45fba03"
#     },
#     "address": "00a329c0648769a73afac7f9381e08fb43dbea72",
#     "name": "Development Account",
#     "meta": "{\"description\":\"Never use this account outside of develoopment chain!\",\"passwordHint\":\"Password is empty string\"}"
# }

# CONSIDER: Use POA instead of POW to shorten block time
# Sample genesis file for clique node:
# {
#   "config": {
#     "chainId": 3762,
#     "homesteadBlock": 1,
#     "eip150Block": 2,
#     "eip150Hash": "0x0000000000000000000000000000000000000000000000000000000000000000",
#     "eip155Block": 3,
#     "eip158Block": 3,
#     "clique": {
#       "period": 15,
#       "epoch": 30000
#     }
#   },
#   "nonce": "0x0",
#   "timestamp": "0x5908570a",
#   "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
#   "extraData": "0x4f6e6469666c6f20436c69717565203337363200000000000000000000000000035e19356880f86804b5fbf7015192be271ab8e426177afe720b3ad16a84d04e195dc6d4a66f82cd801e1cf176afdf340b190a98799666d534f8e953c4849b7564b9763e65f63d0754472374a420af940000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
#   "gasLimit": "0x47b760",
#   "difficulty": "0x1",
#   "mixHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
#   "coinbase": "0x0000000000000000000000000000000000000000",
#   "alloc": {
#     "0000000000000000000000000000000000000000": {
#       "balance": "0x1"
#     },
#   }
# }
