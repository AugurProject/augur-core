#geth init /app/Augur.json
#geth --keystore /app/keystore --password /app/password.txt --unlock "0x9cf532438ec2bd4ad1c3364df4e3a7c4bac8269c,0x1adcbaebf58f2013fbe9cb0ed74a465cb70374a0,c8cfcc9abeaadce1d67d680e3243acceb2dbf845" --mine --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0 --targetgaslimit 6700000 --ethash.dagdir "/app/.ethash"

geth --datadir /app init genesis.json
#geth --no-discover --datadir /app  --keystore /app/keystore --password /app/password.txt --unlock "0xc5ed899b0878656feb06467e2e9ede3ae73cbcb7,0xf8002f7f3ff80b0f2fccbfcc2998d0cda44804e0" --mine --rpcaddr 127.0.0.1 --rpcapi eth,net,web3,personal --targetgaslimit 6500000 --ethash.dagdir "/app/.ethash"
geth --datadir /app  --keystore /app/keystore --password /app/password.txt --unlock "0xc5ed899b0878656feb06467e2e9ede3ae73cbcb7,0xf8002f7f3ff80b0f2fccbfcc2998d0cda44804e0" --mine --networkid=12345 --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0 --targetgaslimit 6700000 --ethash.dagdir "/app/.ethash"
