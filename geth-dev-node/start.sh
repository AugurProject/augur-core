geth --password /app/password.txt account new
geth --password /app/password.txt --unlock 0
geth init /app/genesis.json
geth --mine --networkid=10000 --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0 --targetgaslimit 6700000
