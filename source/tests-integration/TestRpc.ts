import { Configuration } from '../tools/Configuration';
import { Connector } from '../libraries/Connector';
import { server as serverFactory } from 'ethereumjs-testrpc';

export class TestRpc {
    private readonly DEFAULT_TEST_ACCOUNT_BALANCE = 10**20;
    private readonly BLOCK_GAS_LIMIT = 6500000;
    private readonly configuration: Configuration;

    constructor(configuration: Configuration) {
        this.configuration = configuration;
        const accounts = [{ balance: `0x${this.DEFAULT_TEST_ACCOUNT_BALANCE.toString(16)}`, secretKey: configuration.privateKey }];
        const options = { gasLimit: `0x${this.BLOCK_GAS_LIMIT.toString(16)}`, accounts: accounts };
        const testRpcServer = serverFactory(options);
        testRpcServer.listen(configuration.httpProviderPort);
    }

    public waitForStartup = async () => {
        await new Connector(this.configuration).waitUntilConnected();
    }

    public static startTestRpcIfNecessary = async (configuration: Configuration): Promise<void> => {
        if (typeof process.env.ETHEREUM_HOST !== "undefined") return;
        return await new TestRpc(configuration).waitForStartup();
    }
}
