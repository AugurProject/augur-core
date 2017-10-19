FROM ethereum/client-go:latest

COPY genesis.json /geth/genesis.json
RUN printf "\n" > /geth/password.txt
COPY dev-key.json /geth/keys/dev-key.json
RUN geth --datadir /geth init /geth/genesis.json

WORKDIR /
COPY start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT /start.sh

# docker image build --tag geth-dev-node .
# docker container run --rm -it -p 8545:8545 --name geth-dev-node geth-dev-node -p 8545:8545 ethereum/client-go --dev --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0 --targetgaslimit 6500000
# To connect in a separate terminal: geth attach http://127.0.0.1:8545
