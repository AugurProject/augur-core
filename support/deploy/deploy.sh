[[ "${DEPLOY}" == "true" ]] && node output/deployment/deployContracts.js || exit 1
[[ "${ARTIFACTS}" == "true" ]] && npm run artifacts || exit 1
