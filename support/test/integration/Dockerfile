FROM augur/augur-core:latest

ENTRYPOINT [ "npx", "mocha", "output/tests-integration/**/*.js", "--no-timeouts", "--require", "source-map-support/register" ]
