import { URL } from 'url';
import { NetworkConfiguration } from '../libraries/NetworkConfiguration';
import { server as serverFactory, TestRpcServer } from 'ethereumjs-testrpc';

export class TestRpc {
    private readonly DEFAULT_TEST_ACCOUNT_BALANCE = 10**20;
    private readonly BLOCK_GAS_LIMIT = 6500000;
    private readonly networkConfiguration: NetworkConfiguration;
    private readonly testRpcServer: TestRpcServer;

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

    public static startTestRpcIfNecessary = async (networkConfiguration: NetworkConfiguration): Promise<void> => {
        if (networkConfiguration.networkName === 'testrpc') {
            const testRpc = new TestRpc(networkConfiguration);
            testRpc.listen();
        }
    }
}
