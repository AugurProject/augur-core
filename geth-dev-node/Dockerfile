FROM ethereum/client-go:latest
COPY genesis.json /app/genesis.json
COPY UTC--2017-10-16T07-23-03.916747000Z--9cf532438ec2bd4ad1c3364df4e3a7c4bac8269c /app/keystore/UTC--2017-10-16T07-23-03.916747000Z--9cf532438ec2bd4ad1c3364df4e3a7c4bac8269c
RUN echo "" > /app/password.txt
RUN geth makedag 0 /app/.ethash

WORKDIR /
COPY start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT /start.sh

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
