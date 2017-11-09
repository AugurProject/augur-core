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
        console.log(`Processing ${compilerOutput.contracts.length}`)
        for (let relativeFilePath in compilerOutput.contracts) {
            for (let contractName in compilerOutput.contracts[relativeFilePath]) {
                const bytecode = Buffer.from(compilerOutput.contracts[relativeFilePath][contractName].evm.bytecode.object, 'hex');
                const compiledContract = new Contract(relativeFilePath, contractName, compilerOutput.contracts[relativeFilePath][contractName].abi, bytecode);
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

    [Symbol.iterator](): Iterator<Contract> {
        const contracts = this.contracts.values();
        return { next: contracts.next.bind(contracts) }
    }
}
