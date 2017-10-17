import * as binascii from "binascii";
import EthjsAccount = require("ethjs-account");
import EthjsQuery = require('ethjs-query');
import { TransactionReceipt } from 'ethjs-shared';

const DEFAULT_TEST_ACCOUNT_BALANCE = 1 * 10 ** 20; // Denominated in wei
// Set gas block limit extremely high so new blocks don"t have to be mined while uploading contracts
const GAS_BLOCK_AMOUNT = Math.pow(2, 32);
const ETHEREUM_POLLING_INTERVAL_MILLISECONDS = process.env.ETHEREUM_POLLING_INTERVAL_MILLISECONDS ? parseInt(process.env.ETHEREUM_POLLING_INTERVAL_MILLISECONDS!, 10) : 1200;

export interface TestAccount {
    privateKey: string;
    publicKey: string;
    address: string;
}

interface RpcClientAccountOption {
    balance: number;
    secretKey: string;
}

interface RpcClientOptions {
    gasLimit: number;
    accounts: RpcClientAccountOption[];
}

// CONSIDER: Change length from representing number of characters to number of bytes
/**
 * Pads a string with zeros (on the left by default) and converts it to hexidecimal format.
 * @param stringToEncode ASCII string to be padded & hexlified
 * @param length Desired length of the returned string (minus the "0x")
 */
export function padAndHexlify(stringToEncode: string, length: number, direction: string = "left"): string {
    let pad = "";
    for (let i = 0; i < length - (stringToEncode.length * 2); i++) {
        pad += "\x00";
    }
    let paddedStringToEncode: string;
    if (direction === "right") {
        paddedStringToEncode = stringToEncode + pad;
    } else {
        paddedStringToEncode = pad + stringToEncode;
    }
    return "0x" + binascii.hexlify(paddedStringToEncode);
}

export function stringTo32ByteHex(stringToEncode: string): string {
    return padAndHexlify(stringToEncode, 64, "right");
}

export async function generateTestAccounts(secretKeys: string[]): Promise<TestAccount[]> {
    let testAccounts: Promise<TestAccount>[] = [];
    for (let secretKey in secretKeys) {
        const hexlifiedSecretKey = padAndHexlify(secretKeys[secretKey], 64);
        let testAccount = await EthjsAccount.privateToAccount(hexlifiedSecretKey);
        for (let testAccountData in testAccount) {
            testAccount[testAccountData] = testAccount[testAccountData].toLowerCase();
        }
        testAccounts.push(testAccount);
    }

    return await Promise.all(testAccounts);
}

export async function initializeTestRpcClientOptions(ethHttpProviderPort: number, secretKeys: string[]): Promise<RpcClientOptions> {
    // Generate test accounts
    const testAccounts = await generateTestAccounts(secretKeys);

    // Initialize TestRPC account options
    let accountOptions: RpcClientAccountOption[] = [];
    for (let testAccount in testAccounts) {
        accountOptions.push({ balance: DEFAULT_TEST_ACCOUNT_BALANCE, secretKey: testAccounts[testAccount].privateKey });
    }

    return { gasLimit: GAS_BLOCK_AMOUNT, accounts: accountOptions };
}

export async function sleep(milliseconds: number): Promise<void> {
    return new Promise<void>((resolve, reject) => setTimeout(resolve, milliseconds));
}

export async function waitForTransactionReceipt(ethjsQuery: EthjsQuery, transactionHash: string): Promise<TransactionReceipt> {
    let transactionReceipt = await ethjsQuery.getTransactionReceipt(transactionHash);
    while (!transactionReceipt) {
        await sleep(ETHEREUM_POLLING_INTERVAL_MILLISECONDS);
        transactionReceipt = await ethjsQuery.getTransactionReceipt(transactionHash);
    }
    return transactionReceipt;
}
