import * as binascii from "binascii";
import EthjsQuery = require('ethjs-query');
import { TransactionReceipt } from 'ethjs-shared';

const DEFAULT_TEST_ACCOUNT_BALANCE = 1 * 10 ** 20; // Denominated in wei
// Set gas block limit extremely high so new blocks don"t have to be mined while uploading contracts
const GAS_BLOCK_AMOUNT = Math.pow(2, 32);

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

export function initializeTestRpcClientOptions(privateKey: string): RpcClientOptions {
    // Initialize TestRPC account options
    let accountOptions: RpcClientAccountOption[] = [];
    accountOptions.push({ balance: DEFAULT_TEST_ACCOUNT_BALANCE, secretKey: privateKey });
    return { gasLimit: GAS_BLOCK_AMOUNT, accounts: accountOptions };
}

export async function sleep(milliseconds: number): Promise<void> {
    return new Promise<void>((resolve, reject) => setTimeout(resolve, milliseconds));
}

export async function waitForTransactionReceipt(ethjsQuery: EthjsQuery, transactionHash: string, failureDetails: string): Promise<TransactionReceipt> {
    let pollingInterval = 10;
    let receipt = await ethjsQuery.getTransactionReceipt(transactionHash);
    while (!receipt || !receipt.blockHash) {
        await sleep(pollingInterval);
        receipt = await ethjsQuery.getTransactionReceipt(transactionHash);
        pollingInterval = Math.min(pollingInterval*2, 5000);
    }
    const status = (typeof receipt.status === 'number') ? receipt.status : parseInt(receipt.status, 16);
    if (!status) {
        throw new Error(`Transaction failed.  ${failureDetails}`);
    }
    return receipt;
}
