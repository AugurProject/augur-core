import { Abi } from 'ethereum';
import { CompilerOutput } from 'solc';

export class Contract {
    public readonly relativeFilePath: string;
    public readonly contractName: string;
    public readonly abi: Abi;
    public readonly bytecode: Buffer;
    public address?: string;

    public constructor(relativeFilePath: string, contractName: string, abi: Abi, bytecode: Buffer) {
        this.relativeFilePath = relativeFilePath;
        this.contractName = contractName;
        this.abi = abi;
        this.bytecode = bytecode;
    }
}

export class Contracts implements Iterable<Contract> {
    private readonly contracts = new Map<string, Contract>();

    public constructor(compilerOutput: CompilerOutput) {
        for (let relativeFilePath in compilerOutput.contracts) {
            for (let contractName in compilerOutput.contracts[relativeFilePath]) {
                // don't include helper libraries
                if (!relativeFilePath.endsWith(`${contractName}.sol`)) continue;
                const abi = compilerOutput.contracts[relativeFilePath][contractName].abi;
                if (abi === undefined) continue;
                const bytecodeString = compilerOutput.contracts[relativeFilePath][contractName].evm.bytecode.object;
                if (bytecodeString === undefined) continue;
                // don't include interfaces
                if (bytecodeString.length === 0) continue;
                const bytecode = Buffer.from(bytecodeString, 'hex');
                const compiledContract = new Contract(relativeFilePath, contractName, abi, bytecode);
                this.contracts.set(contractName, compiledContract);
            }
        }
    }

    public has = (contractName: string): boolean => {
        return this.contracts.has(contractName);
    }

    public get = (contractName: string): Contract => {
        if (!this.contracts.has(contractName)) throw new Error(`${contractName} does not exist.`);
        return this.contracts.get(contractName)!;
    }

    [Symbol.iterator]() {
        const contracts = this.contracts.values();
        return { next: contracts.next.bind(contracts) }
    }
}
