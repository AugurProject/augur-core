import EthjsHttpProvider = require('ethjs-provider-http');
import EthjsQuery = require('ethjs-query');
import { TransactionReceipt } from 'ethjs-shared';
import { Configuration } from './Configuration';
import { sleep } from './HelperFunctions';

export class Connector {
    public readonly ethjsQuery: EthjsQuery;

    constructor(configuration: Configuration) {
        const ethjsHttpProvider = new EthjsHttpProvider(`http://${configuration.httpProviderHost}:${configuration.httpProviderPort}`);
        this.ethjsQuery = new EthjsQuery(ethjsHttpProvider);
    }

    public async waitUntilConnected(): Promise<EthjsQuery> {
        while (true) {
            try {
                await this.ethjsQuery.net_version();
                break;
            } catch {
                // swallow the error, we just want to loop until the net_version call above succeeds.
            }
        }
        return this.ethjsQuery;
    }

    waitForTransactionReceipt = async (transactionHash: string, failureDetails: string): Promise<TransactionReceipt>  => {
        let pollingInterval = 10;
        let receipt = await this.ethjsQuery.getTransactionReceipt(transactionHash);
        while (!receipt || !receipt.blockHash) {
            await sleep(pollingInterval);
            receipt = await this.ethjsQuery.getTransactionReceipt(transactionHash);
            pollingInterval = Math.min(pollingInterval*2, 5000);
        }
        const status = (typeof receipt.status === 'number') ? receipt.status : parseInt(receipt.status, 16);
        if (!status) {
            throw new Error(`Transaction failed.  ${failureDetails}`);
        }
        return receipt;
    }
}
