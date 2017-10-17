#TODO: Create TOML file rather than using command line parameters
geth --datadir /geth --keystore /geth/keys --password /geth/password.txt --unlock "0xc5ed899b0878656feb06467e2e9ede3ae73cbcb7" --mine --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0 --targetgaslimit 6500000
