import EthjsHttpProvider = require('ethjs-provider-http');
import EthjsQuery = require('ethjs-query');
import { Configuration } from './Configuration';

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
}
