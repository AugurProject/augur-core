import * as getPort from "get-port";
import EthjsHttpProvider = require('ethjs-provider-http');
import EthjsQuery = require('ethjs-query');

export class Connector {
    private ethjsQuery: EthjsQuery|null = null;

    public async getEthjsQuery(): Promise<EthjsQuery> {
        if (this.ethjsQuery === null) {
            this.ethjsQuery = await this.connect();
        }
        return this.ethjsQuery;
    }

    public async waitUntilConnected(): Promise<EthjsQuery> {
        const ethjsQuery = await this.getEthjsQuery();
        while (true) {
            try {
                await ethjsQuery.net_version();
                break;
            } catch {
                // swallow the error, we just want to loop until the net_version call above succeeds.
            }
        }
        return ethjsQuery;
    }

    private async connect(): Promise<EthjsQuery> {
        const ethjsHttpProviderHost = (typeof process.env.ETHEREUM_HOST === "undefined") ? "localhost" : process.env.ETHEREUM_HOST;
        const ethjsHttpProviderPort = (typeof process.env.ETHEREUM_PORT === "undefined") ? await getPort() : parseInt(process.env.ETHEREUM_PORT || "0");
        const ethjsHttpProvider = new EthjsHttpProvider(`http://${ethjsHttpProviderHost}:${ethjsHttpProviderPort}`);
        const ethjsQuery = new EthjsQuery(ethjsHttpProvider);
        return ethjsQuery;
    }
}
