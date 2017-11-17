[[ "${DEPLOY}x" == "true" ]] && node output/deployment/deployContracts.js
[[ "${ARTIFACTS}x" == "true" ]] && npm run artifacts
