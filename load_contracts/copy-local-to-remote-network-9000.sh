# ssh jack@45.33.62.72 sudo service geth stop
ssh jack@45.33.62.72 rm -Rf /home/jack/.ethereum-9000/geth/chaindata
scp -rp $HOME/.ethereum-9000/geth/chaindata jack@45.33.62.72:/home/jack/.ethereum-9000/geth/chaindata
ssh jack@45.33.62.72 sudo service geth start
