# TODO: Figure out if there's a way to pre-generate DAG.
# Calling `RUN geth makedag 0 /app/.ethash` in the Dockerfile to pre-generate DAG
# followed by `--ethash.dagdir "/app/.ethash"` when mining in start.sh produced:

# System clock seems off by -XXXXXs, which can prevent network connectivity
#Please enable network time synchronisation in system settings

FROM ethereum/client-go:latest
COPY genesis.json /app/genesis.json
COPY password.txt /app/password.txt

WORKDIR /
COPY start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT /start.sh

#WORKING: docker run -p 8545:8545 new-test --networkid=10000 --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0 --targetgaslimit 6700000 --mine

# docker build . -t geth-dev-node
# docker run --rm -it -p 8545:8545 geth-dev-node --networkid=10000 --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0 --targetgaslimit 6700000 --mine
