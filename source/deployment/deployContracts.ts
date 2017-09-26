#!/usr/bin/env node

import * as fs from 'async-file';
import * as path from 'path';
import * as HttpProvider from 'ethjs-provider-http';
import * as Eth from 'ethjs-query';
import * as EthContract from 'ethjs-contract';
import { ContractBlockchainData } from 'contract-deployment';
import { SolidityContractCompiler } from "../libraries/CompileSolidity";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { RpcClient } from "../libraries/RpcClient";

const CONTRACT_INPUT_DIR_PATH = path.join(__dirname, "../../source/contracts");
const CONTRACT_OUTPUT_DIR_PATH = path.join(__dirname, "../contracts");
const COMPILED_CONTRACT_OUTPUT_FILE_NAME = "augurCore";
const GAS_AMOUNT = 3000000;
const DEFAULT_ETHEREUM_PORT = 8545;


export async function compileAndDeployContracts(): Promise<ContractBlockchainData[]> {
    // Compile contracts to a single output file
    const solidityContractCompiler = new SolidityContractCompiler(CONTRACT_INPUT_DIR_PATH, CONTRACT_OUTPUT_DIR_PATH, COMPILED_CONTRACT_OUTPUT_FILE_NAME);
    const compilerResult = await solidityContractCompiler.compileContracts();

    // Initialize Ethereum node details.  (If no host is specified, TestRPC will be used.)
    const httpProviderport = (typeof process.env.ETHEREUM_PORT == 'undefined') ? DEFAULT_ETHEREUM_PORT : process.env.ETHEREUM_PORT;
    if (typeof process.env.ETHEREUM_HOST == 'undefined') {
        const rpcClient = new RpcClient();
        await rpcClient.listen(httpProviderport);
    }

    // Initialize Eth object
    const httpProviderUrl = "http://localhost:" + httpProviderport;
    const eth = new Eth(new HttpProvider(httpProviderUrl));
    const accounts = await eth.accounts();
    const fromAccount = accounts[0];

    // Read in contract ABIs and bytecodes as JSON string
    const contractJson = await fs.readFile(CONTRACT_OUTPUT_DIR_PATH + "/" + COMPILED_CONTRACT_OUTPUT_FILE_NAME, "utf8");

    // Deploy contracts to blockchain
    const contractDeployer = new ContractDeployer();
    const contracts = await contractDeployer.deployContracts(eth, contractJson, fromAccount, GAS_AMOUNT);

    return contracts;
}


// If this script is not being imported by another module (i.e., it is being run independently via the command line)
if (!module.parent) {
    compileAndDeployContracts().then(() => {
        process.exit();
    }).catch(error => {
        console.log(error);
        process.exit();
    });
}
