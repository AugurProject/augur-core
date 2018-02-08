declare module 'ethjs-rpc' {
    import HttpProvider = require('ethjs-provider-http');

    class EthjsRpc {
        constructor(provider: HttpProvider);
        sendAsync(details: { method: string, params: any[] }): Promise<any>;
    }

    export = EthjsRpc;
}
