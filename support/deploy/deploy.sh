[[ "${DEPLOY}" == "true" ]] && node output/deployment/deployContracts.js
[[ "${ARTIFACTS}" == "true" ]] && npm run artifacts
