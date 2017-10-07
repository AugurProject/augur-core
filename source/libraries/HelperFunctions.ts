import * as binascii from "binascii";
import * as EthjsAccount from "ethjs-account";

const DEFAULT_TEST_ACCOUNT_BALANCE = 100000000;
// Set gas block limit extremely high so new blocks don"t have to be mined while uploading contracts
const GAS_BLOCK_AMOUNT = Math.pow(2, 32);

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

/**
 * Pads a string with zeros on the left and converts it to hexidecimal format.
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

export async function generateTestAccounts(secretKeys: string[]): Promise<TestAccount[]> {
    let testAccounts: Promise<TestAccount>[] = [];
    for (let secretKey in secretKeys) {
        const hexlifiedSecretKey = await padAndHexlify(secretKeys[secretKey], 64);
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
