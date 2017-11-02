declare module 'ethjs-shared' {
    import BN = require('bn.js');
    export type Primitive = 'uint256' | 'uint64' | 'uint8' | 'bool' | 'string' | 'address' | 'bytes32' | 'bytes';

    export interface AbiParameter {
        name: string,
        type: Primitive,
    }

    export interface AbiEventParameter extends AbiParameter {
        indexed: boolean,
    }

    export interface AbiFunction {
        name: string,
        type: 'function',
        stateMutability: 'pure' | 'constant' | 'view' | 'payable' | 'nonpayable',
        constant: boolean,
        payable: boolean,
        inputs: AbiParameter[],
        outputs: AbiParameter[],
    }

    export interface AbiEvent {
        name: string,
        type: 'event',
        inputs: AbiEventParameter[],
        anonymous: boolean,
    }

    export type Abi = AbiFunction | AbiEvent;

    export interface Transaction {
        from?: string;
        to?: string;
        gas?: BN;
        gasPrice?: BN;
        value?: BN;
        data?: string;
        nonce?: BN;
    }

    export interface TransactionReceipt {
        transactionHash: string;
        transactionIndex: BN;
        blockHash: string;
        blockNumber: BN;
        cumulativeGasUsed: BN;
        gasUsed: BN;
        contractAddress: string;
        logs: Array<Log>;
        status: number|string;
    }

    export interface Block {
        number: BN;
        hash: string;
        parentHash: string;
        nonce: string;
        sha3Uncles: string;
        logsBloom: string;
        transactionRoot: string;
        stateRoot: string;
        receiptRoot: string;
        miner: string;
        difficult: BN;
        totalDifficulty: BN;
        extraData: string;
        size: BN;
        gasLimit: BN;
        gasUsed: BN;
        timestamp: BN;
        transactions: Array<TransactionReceipt>;
        uncles: Array<string>;
    }

    export interface Log {
        removed: boolean;
        logIndex: BN;
        transactionIndex: BN;
        transactionHash: string;
        blockHash: string;
        blockNumber: BN;
        address: string;
        data: string;
        topics: Array<string>;
    }
}
