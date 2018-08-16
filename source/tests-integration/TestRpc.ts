import { URL } from 'url';
import { NetworkConfiguration } from '../libraries/NetworkConfiguration';
import { server as serverFactory } from '@velma/ganache-core';
import { CompilerOutput } from 'solc';
import { CompilerConfiguration } from '../libraries/CompilerConfiguration';

 export async function sleep(milliseconds: number): Promise<void> {
    return new Promise<void>(resolve => setTimeout(resolve, milliseconds));
}

export class TestRpc {
    private readonly DEFAULT_TEST_ACCOUNT_BALANCE = 10**20;
    private readonly BLOCK_GAS_LIMIT = 6500000;
    private readonly BLOCK_GAS_LIMIT_SDB = 20000000;
    private readonly networkConfiguration: NetworkConfiguration;
    private readonly compilerConfiguration: CompilerConfiguration;
    private readonly testRpcServer: any;

    private static instance : TestRpc | null = null;

    constructor(networkConfiguration: NetworkConfiguration, compilerConfiguration: CompilerConfiguration) {
        this.networkConfiguration = networkConfiguration;
        this.compilerConfiguration = compilerConfiguration;
        const sdbPort: number | null = process.env.SDB_PORT ? parseInt(process.env.SDB_PORT!) : null;
        const blockGasLimit = this.compilerConfiguration.enableSdb ? this.BLOCK_GAS_LIMIT_SDB : this.BLOCK_GAS_LIMIT;
        const accounts = [{ balance: `0x${this.DEFAULT_TEST_ACCOUNT_BALANCE.toString(16)}`, secretKey: networkConfiguration.privateKey }];
        let options: any = { gasLimit: `0x${blockGasLimit.toString(16)}`, accounts: accounts, sdb: this.compilerConfiguration.enableSdb };
        if (sdbPort !== null) {
            options.sdbPort = sdbPort;
        }
        this.testRpcServer = serverFactory(options);
    }

    public listen(): void {
        const url = new URL(this.networkConfiguration.http);
        this.testRpcServer.listen(parseInt(url.port) || 80);
    }

    public static startTestRpcIfNecessary = async (networkConfiguration: NetworkConfiguration, compilerConfiguration: CompilerConfiguration): Promise<TestRpc | null> => {
        if (networkConfiguration.networkName === 'testrpc') {
            if (TestRpc.instance !== null) return TestRpc.instance;
            TestRpc.instance = new TestRpc(networkConfiguration, compilerConfiguration);
            TestRpc.instance.listen();
            if (compilerConfiguration.enableSdb) {
                await TestRpc.instance.waitForSdb();
            }
            return TestRpc.instance;
        } else {
            return null;
        }
    }

    private waitForSdb = async (): Promise<void> => {
        while (true) {
            const isReady = await this.sdbReady();
            if (isReady) return;
            await sleep(2000);
        }
    }

    private sdbReady = async (): Promise<boolean> => {
        return new Promise<boolean>((resolve, reject) => {
            const sdbHook = this.testRpcServer.provider.manager.state.sdbHook;
            if (sdbHook) {
                sdbHook.ping(resolve);
            }
            else {
                reject("sdbHook isn't defined. Are you sure you initialized testrpc/ganache-core properly?")
            }
        });
    }

    public linkDebugSymbols = async (compilerOutput: CompilerOutput, addressMapping: any): Promise<void> => {
        await this.linkCompilerOutput(compilerOutput);
        const keys = Object.keys(addressMapping);
        for (let i = 0; i < keys.length; i++) {
            const contractName = keys[i];
            await this.linkContractAddress(contractName, addressMapping[keys[i]]);
                }
            }
             public linkCompilerOutput = async (compilerOutput: CompilerOutput): Promise<void> => {
        return new Promise<void>((resolve, reject) => {
            const sdbHook = this.testRpcServer.provider.manager.state.sdbHook;
            if (sdbHook) {
                sdbHook.linkCompilerOutput(this.compilerConfiguration.contractSourceRoot, compilerOutput, resolve);
            }
            else {
                reject("sdbHook isn't defined. Are you sure you initialized testrpc/ganache-core properly?")
            }
        });
    }

    public linkContractAddress = async (name: string, address: string): Promise<void> => {
        return new Promise<void>((resolve, reject) => {
            const sdbHook = this.testRpcServer.provider.manager.state.sdbHook;
            if (sdbHook) {
                sdbHook.linkContractAddress(name, address, resolve);
            }
            else {
                reject("sdbHook isn't defined. Are you sure you initialized testrpc/ganache-core properly?")
            }
        });
    }
}
