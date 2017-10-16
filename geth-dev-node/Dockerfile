FROM ethereum/client-go:latest

RUN mkdir /home/\.ethereum
RUN mkdir /home/\.ethereum/keystore
RUN mkdir /home/\.ethash

COPY genesis.json /home/genesis.json
RUN printf "\n" > /home/password.txt
# Sealing account (pre-funded with a large balance)
COPY UTC--2017-10-16T19-13-42.464934000Z--c5ed899b0878656feb06467e2e9ede3ae73cbcb7 /home/\.ethereum/keystore/UTC--2017-10-16T19-13-42.464934000Z--c5ed899b0878656feb06467e2e9ede3ae73cbcb7

WORKDIR /
COPY start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT /start.sh

# docker build -t geth-dev-node .
# docker run --rm -it -p 8545:8545 geth-dev-node -p 8545:8545 ethereum/client-go --dev --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0 --targetgaslimit 6500000
# To connect in a separate terminal: geth attach http://127.0.0.1:8545
