FROM ethereum/client-go:latest
COPY genesis.json /app/genesis.json
RUN printf "\n\n" > /app/password.txt
# Sealing account
COPY UTC--2017-10-16T19-13-42.464934000Z--c5ed899b0878656feb06467e2e9ede3ae73cbcb7 /app/keystore/UTC--2017-10-16T19-13-42.464934000Z--c5ed899b0878656feb06467e2e9ede3ae73cbcb7
# Prefunded account
COPY UTC--2017-10-16T19-14-03.632603000Z--f8002f7f3ff80b0f2fccbfcc2998d0cda44804e0 /app/keystore/UTC--2017-10-16T19-14-03.632603000Z--f8002f7f3ff80b0f2fccbfcc2998d0cda44804e0
#RUN geth makedag 0 /app/.ethash

WORKDIR /
COPY start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT /start.sh

# docker build --tag geth-dev-node .
# docker run --rm -it -p 8545:8545 geth-dev-node -p 8545:8545 ethereum/client-go --dev --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0
