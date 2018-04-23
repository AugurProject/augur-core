#!/usr/bin/env node

// NOTE: Make sure to run with --max-old-space-size=12288. We're loading a massive file into memory during report generation

const App = require('solidity-coverage/lib/app.js');
const death = require('death');
const { execSync } = require('child_process');
const copydir = require('copy-dir');
const replace = require("replace");
const rimraf = require('rimraf');
const fs = require('fs');

const config = {
    dir: './source',
    skipFiles: [],
    copyNodeModules: false,
}

const app = new App(config);
app.postProcessPure = function () {};

death((signal, err) => app.cleanUp(err));

app.generateCoverageEnvironment();

app.instrumentTarget();

rimraf.sync('./coverageEnv/solidity_test_helpers');
fs.mkdirSync('./coverageEnv/solidity_test_helpers')

copydir.sync('./tests/solidity_test_helpers', './coverageEnv/solidity_test_helpers')

replace({
    regex: " view | pure ",
    replacement: " ",
    paths: fs.readdirSync('./coverageEnv/solidity_test_helpers').map(filename => './coverageEnv/solidity_test_helpers/' + filename),
    silent: false,
})

try {
    execSync('pytest --cover', {stdio:[0,1,2]});
} catch (err) {
    console.log(err);
}

app.generateReport();

// Cleanup
rimraf.sync('./allFiredEvents');
rimraf.sync('./scTopics');
rimraf.sync('./coverage.json');
rimraf.sync('./tests/compilation_cache')
