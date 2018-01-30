import { NetworkConfiguration } from '../libraries/NetworkConfiguration';
import { Connector } from '../libraries/Connector';
import { server as serverFactory } from 'ethereumjs-testrpc';

export class TestRpc {
    private readonly DEFAULT_TEST_ACCOUNT_BALANCE = 10**20;
    private readonly BLOCK_GAS_LIMIT = 6500000;
    private readonly networkConfiguration: NetworkConfiguration;

    constructor(networkConfiguration: NetworkConfiguration) {
        this.networkConfiguration = networkConfiguration;
        const accounts = [{ balance: `0x${this.DEFAULT_TEST_ACCOUNT_BALANCE.toString(16)}`, secretKey: networkConfiguration.privateKey }];
        const options = { gasLimit: `0x${this.BLOCK_GAS_LIMIT.toString(16)}`, accounts: accounts };
        const testRpcServer = serverFactory(options);
        testRpcServer.listen(networkConfiguration.port);
    }

    public waitForStartup = async () => {
        await new Connector(this.networkConfiguration).waitUntilConnected();
    }

    public static startTestRpcIfNecessary = async (networkConfiguration: NetworkConfiguration): Promise<void> => {
        if (typeof process.env.ETHEREUM_HOST !== "undefined") return;
        return await new TestRpc(networkConfiguration).waitForStartup();
    }
}
