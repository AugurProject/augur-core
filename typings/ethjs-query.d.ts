declare module 'ethjs-query' {
    import EthjsHttpProvider = require('ethjs-provider-http');
    import EthjsRpc = require('ethjs-rpc');
    import { Abi, TransactionForSend, TransactionForCall, TransactionReceipt, BN as BNInterface, Log } from 'ethjs-shared';

    class EthjsQuery {
        constructor(provider: EthjsHttpProvider);
        accounts(): Promise<Array<string>>;
        contract(abi: Abi[], bytecode?: string, defaultTransactionObject?: TransactionForSend): any;
        estimateGas(transaction: TransactionForCall): Promise<BNInterface>;
        getBalance(address: string): Promise<BNInterface>;
        getBlockByNumber(blockNumber: number|"earliest"|"latest"|"pending", returnFullBlock: boolean);
        getLogs(options: { fromBlock: BNInterface | string, toBlock: BNInterface | string, address: string, topics: (string | null)[] }): Log[];
        getTransactionReceipt(transactionHash: string): Promise<TransactionReceipt>;
        net_version(): string;
        rpc: EthjsRpc;
    }

    namespace EthjsQuery {
        class BN extends BNInterface {
            constructor(value: number | string, radix?: number)
        }

        const keccak256: (source: string) => string;
    }

    export = EthjsQuery;
}
