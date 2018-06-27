import { URL } from 'url';
import { NetworkConfiguration } from '../libraries/NetworkConfiguration';
import { server as serverFactory } from 'ganache-core';

export class TestRpc {
    private readonly DEFAULT_TEST_ACCOUNT_BALANCE = 10**20;
    private readonly BLOCK_GAS_LIMIT = 6500000;
    private readonly networkConfiguration: NetworkConfiguration;
    private readonly testRpcServer: any;

    private static instance : TestRpc | null = null;

    constructor(networkConfiguration: NetworkConfiguration) {
        this.networkConfiguration = networkConfiguration;
        const accounts = [{ balance: `0x${this.DEFAULT_TEST_ACCOUNT_BALANCE.toString(16)}`, secretKey: networkConfiguration.privateKey }];
        const options = { gasLimit: `0x${this.BLOCK_GAS_LIMIT.toString(16)}`, accounts: accounts };
        this.testRpcServer = serverFactory(options);
    }

    public listen(): void {
        const url = new URL(this.networkConfiguration.http);
        this.testRpcServer.listen(parseInt(url.port) || 80);
    }

    public static startTestRpcIfNecessary = async (networkConfiguration: NetworkConfiguration): Promise<TestRpc | null> => {
        if (networkConfiguration.networkName === 'testrpc') {
            if (TestRpc.instance !== null) return TestRpc.instance;
            TestRpc.instance = new TestRpc(networkConfiguration);
            TestRpc.instance.listen();
            return TestRpc.instance;
        } else {
            return null;
        }
    }
}
