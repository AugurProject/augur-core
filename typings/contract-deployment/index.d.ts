declare module 'contract-deployment' {
    interface ContractBlockchainData {
        abi: any;
        query: any;
        address: string;
        bytecode: string;
        defaultTxObject: any;
        filters: any;
        // TODO: Figure out how to specify in TypeScript that ContractBlockchainData can have any number of functions
    }

    interface ContractReceipt {
        transactionHash: string;
        transactionIndex: any;
        blockHash: string;
        blockNumber: any;
        gasUsed: any;
        cumulativeGasUsed: any;
        contractAddress: string;
        logs: any;
    }
}
