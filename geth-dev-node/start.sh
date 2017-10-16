geth init /app/genesis.json
geth --keystore /app/keystore --password /app/password.txt --unlock 0x9cf532438ec2bd4ad1c3364df4e3a7c4bac8269c --mine --networkid=10000 --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0 --targetgaslimit 6700000 --ethash.dagdir "/app/.ethash"
