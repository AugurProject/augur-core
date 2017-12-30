echo "Deploying Augur to $ETHEREUM_NETWORK"
port="8545"
case $ETHEREUM_NETWORK in
  "ropsten")
    host="ropsten.augur.net"
    privateKey=$ROPSTEN_PRIVATE_KEY
    gasPrice=20
    ;;
  "rinkeby")
    host="rinkeby.ethereum.origin.augur.net"
    port="8545"
    privateKey=$RINKEBY_PRIVATE_KEY
    gasPrice=20
    ;;
  "kovan")
    host="kovan.augur.net"
    privateKey=$KOVAN_PRIVATE_KEY
    gasPrice=1
    ;;
  "rockaway")
    host="localhost"
    privateKey=$ROCKAWAY_PRIVATE_KEY
    gasPrice=1
    ;;
  "clique")
    host="clique.ethereum.nodes.augur.net"
    port="80"
    privateKey="fae42052f82bed612a724fec3632f325f377120592c75bb78adfcceae6470c5a"
    gasPrice=1
    ;;
  "aura")
    host="aura.ethereum.nodes.augur.net"
    port="80"
    privateKey="47f49c399482f73143cadeb2db8938d3f249578bdc64cdcda4ecf1ee535a5c91"
    gasPrice=1
    ;;
  *)
    echo "Must specify a network to deploy"
    exit 1
    ;;
esac

export ETHEREUM_GAS_PRICE_IN_NANOETH=$gasPrice
export ETHEREUM_HOST=$host
export ETHEREUM_PORT=$port
export ETHEREUM_PRIVATE_KEY=$privateKey

if [[ "${DEPLOY:-true}" == "true" ]]; then
  node output/deployment/deployContracts.js
  if [[ "$?" != "0" ]]; then
    echo "Error while deploying contracts to $ETHEREUM_NETWORK, exiting and skipping artifact management"
  end
else
  echo "Skipping deploy, set DEPLOY=true to do it"
fi

if [[ "${ARTIFACTS:-true}" == "true" ]]; then
  npm run artifacts || exit 1
else
  echo "Skipping pushing build artificats, set ARTIFACTS=true to do it"
fi
