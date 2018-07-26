export type Primitive = 'uint8' | 'uint32' | 'uint64' | 'uint96' | 'uint128' |'uint256' | 'bool' | 'string' | 'address' | 'bytes12' | 'bytes20' | 'bytes32' | 'bytes' | 'int256' | 'address[]' | 'uint256[]' | 'bytes32[]' | 'bytes32[5]' | 'bytes32[10]' | 'bytes32[20]' | 'bytes32[50]' | 'bytes32[100]' | 'bytes32[200]' | 'bytes32[500]' | 'bytes32[1000]';

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
