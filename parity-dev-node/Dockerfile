FROM parity/parity:v1.7.4

# install all dependencies
RUN apt-get update \
	&& apt-get install --yes --no-install-recommends curl \
	&& rm -rf /var/lib/apt/lists/*

# create the master account
RUN /parity/parity daemon /parity/parity.pid --chain dev --no-ui --no-dapps --no-discovery --jsonrpc-apis web3,eth,net,personal,parity,parity_set,traces,rpc,parity_accounts \
	&& while ! curl --silent --show-error -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"parity_newAccountFromPhrase","params":["",""],"id": 1}' localhost:8545; do sleep 0.1; done \
	&& kill -s TERM `cat /parity/parity.pid` \
	&& while kill -0 `cat /parity/parity.pid`; do sleep 0.01; done \
	&& rm /parity/parity.pid \
	&& echo "" > /parity/password

WORKDIR /
ENTRYPOINT /parity/parity \
	--chain dev \
	--gasprice 2 \
	--no-discovery \
	--force-ui --ui-no-validation --ui-interface 0.0.0.0 \
	--jsonrpc-interface all --jsonrpc-cors "*" --jsonrpc-hosts all --jsonrpc-apis web3,eth,net,personal,parity,parity_set,traces,rpc,parity_accounts \
	--unlock 0x00a329c0648769a73afac7f9381e08fb43dbea72 --password /parity/password

# docker build --tag parity-dev-node .
# docker run --rm -it -p 8000:8000 -p 8001:8001 -p 8545:8545 -p 8180:8180 parity-dev-node
