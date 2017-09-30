#!/usr/bin/env node

import * as fs from "async-file";
import * as binascii from "binascii";
import * as path from "path";
import * as HttpProvider from "ethjs-provider-http";
import * as Eth from "ethjs-query";
import * as EthContract from "ethjs-contract";
import { ContractBlockchainData } from "contract-deployment";
import { SolidityContractCompiler } from "../libraries/CompileSolidity";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { RpcClient } from "../libraries/RpcClient";

const CONTRACT_INPUT_DIR_PATH = path.join(__dirname, "../../source/contracts");
const CONTRACT_OUTPUT_DIR_PATH = path.join(__dirname, "../../output/contracts");
const COMPILED_CONTRACT_OUTPUT_FILE_NAME = "augurCore";
const DEFAULT_ETHEREUM_PORT = 8545;
const DEFAULT_TEST_ACCOUNT_BALANCE = 100000000;
// Set gas block limit extremely high so new blocks don"t have to be mined while uploading contracts
const GAS_BLOCK_AMOUNT = Math.pow(2, 32);
const GAS_AMOUNT = 6400000;

/**
 * Helper method that pads a string with zeros on the left and converts it to hexidecimal format.
 * @param stringToEncode ASCII string to be padded & hexlified
 * @param length Desired length of the returned string (minus the "0x")
 */
export async function padAndHexlify(stringToEncode: string, length: number): Promise<string> {
    let pad = "";
    for (let i = 0; i < length - (stringToEncode.length * 2); i++) {
        pad += "\x00";
    }
    const paddedStringToEncode = pad + stringToEncode;
    return "0x" + binascii.hexlify(paddedStringToEncode);
}

export async function compileAndDeployContracts(): Promise<ContractBlockchainData[]> {
    // Compile contracts to a single output file
    const solidityContractCompiler = new SolidityContractCompiler(CONTRACT_INPUT_DIR_PATH, CONTRACT_OUTPUT_DIR_PATH, COMPILED_CONTRACT_OUTPUT_FILE_NAME);
    const compilerResult = await solidityContractCompiler.compileContracts();

    // Initialize Ethereum node details.  (If no host is specified, TestRPC will be used.)
    const httpProviderport = (typeof process.env.ETHEREUM_PORT == "undefined") ? DEFAULT_ETHEREUM_PORT : process.env.ETHEREUM_PORT;
    if (typeof process.env.ETHEREUM_HOST == "undefined") {
        const privateKey = "Augur";
        const hexlifiedPrivateKey = await padAndHexlify(privateKey, 64);

        // This sets the account balance & private key for test accounts
        const accountArray = [{balance: DEFAULT_TEST_ACCOUNT_BALANCE, secretKey: hexlifiedPrivateKey}];
        const options = {gasLimit: GAS_BLOCK_AMOUNT, accounts: accountArray};

        const rpcClient = new RpcClient();
        await rpcClient.listen(httpProviderport, options);
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
    await contractDeployer.initialize(eth, contractJson, fromAccount, GAS_AMOUNT);

    return contractDeployer.getUploadedContracts();
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
