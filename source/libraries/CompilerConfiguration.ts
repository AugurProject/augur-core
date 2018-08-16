import * as path from 'path';

export class CompilerConfiguration {
    public readonly contractSourceRoot: string;
    public readonly outputRoot: string;
    public readonly contractInterfacesOutputPath: string;
    public readonly abiOutputPath: string
    public readonly contractOutputPath: string
    public readonly enableSdb: boolean;

    public constructor(contractSourceRoot: string, outputRoot: string, enableSdb: boolean = false) {
        this.contractSourceRoot = contractSourceRoot;
        this.outputRoot = outputRoot;
        this.contractInterfacesOutputPath = path.join(contractSourceRoot, '../libraries', 'ContractInterfaces.ts');
        this.abiOutputPath = path.join(outputRoot, 'abi.json');
        this.contractOutputPath = path.join(outputRoot, 'contracts.json');
        this.enableSdb = enableSdb;
    }

    public static create(): CompilerConfiguration {
        const contractSourceRoot = path.join(__dirname, "../../source/contracts/");
        const outputRoot = (typeof process.env.OUTPUT_PATH === "undefined") ? path.join(__dirname, "../../output/contracts/") : path.normalize(<string> process.env.OUTPUT_ROOT);
        const enableSdb = (typeof process.env.ENABLE_SOLIDITY_DEBUG === "undefined") ? false : process.env.ENABLE_SOLIDITY_DEBUG === "true";

        return new CompilerConfiguration(contractSourceRoot, outputRoot, enableSdb);
    }
}
