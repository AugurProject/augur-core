if [[ "${DEPLOY}" == "true" ]]; then
  node output/deployment/deployContracts.js || exit 1
else
  echo "Skipping deploy, set DEPLOY=true to do it"
fi

if [[ "${ARTIFACTS}" == "true" ]]; then
  npm run artifacts || exit 1
else
  echo "Skipping pushing build artificats, set ARTIFACTS=true to do it"
fi
