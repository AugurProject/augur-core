#!/usr/bin/env node

import * as fs from "async-file";
import * as getPort from "get-port";
import * as path from "path";
import * as EthjsHttpProvider from "ethjs-provider-http";
import * as EthjsQuery from "ethjs-query";
import { SolidityContractCompiler } from "../libraries/CompileSolidity";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { initializeTestRpcClientOptions } from "../libraries/HelperFunctions";
import { RpcClient } from "../libraries/RpcClient";

const CONTRACT_INPUT_DIR_PATH = path.join(__dirname, "../../source/contracts");
const CONTRACT_OUTPUT_DIR_PATH = path.join(__dirname, "../../output/contracts");
const COMPILED_CONTRACT_OUTPUT_FILE_NAME = "augurCore";

export async function compileAndDeployContracts(): Promise<ContractDeployer> {
    // Compile contracts to a single output file
    const solidityContractCompiler = new SolidityContractCompiler(CONTRACT_INPUT_DIR_PATH, CONTRACT_OUTPUT_DIR_PATH, COMPILED_CONTRACT_OUTPUT_FILE_NAME);
    const compilerOutput = await solidityContractCompiler.compileContracts();

    const ethjsHttpProviderHost = (typeof process.env.ETHEREUM_PORT === "undefined") ? "localhost" : process.env.ETHEREUM_HOST;
    const ethjsHttpProviderPort = (typeof process.env.ETHEREUM_PORT === "undefined") ? await getPort() : parseInt(process.env.ETHEREUM_PORT || "0");
    const gasPrice = ((typeof process.env.ETHEREUM_GAS_PRICE_IN_NANOETH === "undefined") ? 20 : parseInt(process.env.ETHEREUM_GAS_PRICE || "20")) * 10**9;
    // If no Ethereum host has been specified, use TestRPC.
    if (typeof process.env.ETHEREUM_HOST === "undefined") {
        const testRpcOptions = await initializeTestRpcClientOptions(ethjsHttpProviderPort, ["Augur0"]);
        const rpcClient = new RpcClient();
        await rpcClient.listen(ethjsHttpProviderPort, testRpcOptions);
    }
    const ethjsHttpProvider = new EthjsHttpProvider(`http://${ethjsHttpProviderHost}:${ethjsHttpProviderPort}`);
    const ethjsQuery = new EthjsQuery(ethjsHttpProvider);
    const contractDeployer = new ContractDeployer(ethjsQuery, compilerOutput, gasPrice);
    await contractDeployer.deploy();

    return contractDeployer;
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
