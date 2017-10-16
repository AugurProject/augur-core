geth --datadir /home/\.ethereum init /home/genesis.json
geth --datadir /home/\.ethereum --keystore /home/\.ethereum/keystore --password /home/password.txt --unlock "0xc5ed899b0878656feb06467e2e9ede3ae73cbcb7,0xf8002f7f3ff80b0f2fccbfcc2998d0cda44804e0" --mine --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0 --targetgaslimit 6500000
