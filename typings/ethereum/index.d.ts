export type Primitive = 'uint8' | 'uint64' | 'uint256' | 'bool' | 'string' | 'address' | 'bytes20' | 'bytes32' | 'bytes' | 'int256' | 'address[]' | 'uint256[]' | 'bytes32[]';

export interface AbiParameter {
    name: string,
    type: Primitive,
}

export interface AbiEventParameter extends AbiParameter {
    indexed: boolean,
}

export interface AbiFunction {
    name: string,
    type: 'function' | 'constructor' | 'fallback',
    stateMutability: 'pure' | 'view' | 'payable' | 'nonpayable',
    constant: boolean,
    payable: boolean,
    inputs: Array<AbiParameter>,
    outputs: Array<AbiParameter>,
}

export interface AbiEvent {
    name: string,
    type: 'event',
    inputs: Array<AbiEventParameter>,
    anonymous: boolean,
}

export type Abi = Array<AbiFunction | AbiEvent>;
