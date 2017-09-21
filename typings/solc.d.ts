declare module 'solc' {
    interface CompilerInputSourceFile {
        keccak256?: string;
        urls: string[];
    }
    interface CompilerInputSourceCode {
        keccak256?: string;
        content: string;
    }
    interface CompilerInput {
        language: "Solidity" | "serpent" | "lll" | "assembly";
        sources: {
            [globalName: string]: CompilerInputSourceFile|CompilerInputSourceCode,
        };
    }
    interface CompilerOutputError {
        sourceLocation?: {
            file: string;
            start: number;
            end: number;
        };
        type: "TypeError" | "InternalCompilerError" | "Exception";
        component: "general" | "ewasm";
        severity: "error" | "warning";
        message: string;
        formattedMessage?: string;
    }
    interface CompilerOutputContractAbi {
        constant: boolean;
        inputs: {name: string, type: string}[];
    }
    interface CompilerOutputEvmBytecode {
        object: string;
        opcodes: string;
        sourceMap: string;
        linkReferences: {} | {
            [globalName: string]: {
                [name: string]: {start: number, length: number}[];
            };
        };
    }
    interface CompilerOutput {
        errors?: CompilerOutputError[];
        sources: {
            [globalName: string]: {
                id: number;
                ast: any;
                legacyAST: any;
            },
        };
        contracts: {
            [globalName: string]: {
                abi: CompilerOutputContractAbi[];
                metadata: string;
                userdoc: any;
                devdoc: any;
                ir: string;
                evm: {
                    assembly: string;
                    legacyAssembly: any;
                    bytecode: CompilerOutputEvmBytecode;
                    deployedBytecode: CompilerOutputEvmBytecode;
                    methodIdentifiers: {
                        [methodName: string]: string;
                    };
                    gasEstimates: {
                        creation: {
                            codeDepositCost: string;
                            executionCost: string;
                            totalCost: string;
                        };
                        external: {
                            [functionSignature: string]: string;
                        };
                        internal: {
                            [functionSignature: string]: string;
                        };
                    };
                };
                ewasm: {
                    wast: string;
                    wasm: string;
                }
            };
        };
    }
    type ReadCallback = (path: string) => { contents?: string, error?: string};
    function compileStandardWrapper(input: string, readCallback?: ReadCallback);
}
