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
        settings?: any,
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
        type: "function"|"constructor"|"fallback"|"event";
        name: string;
        constant: boolean;
        inputs: { name: string, type: string }[];
    }
    interface CompilerOutputContractAbiFunction extends CompilerOutputContractAbi {
        type: "function"|"constructor"|"fallback";
        outputs?: { name: string, type: string }[];
        payable: boolean;
        stateMutability: "pure"|"view"|"nonpayable"|"payable";
        constant: boolean;
    }
    interface CompilerOutputContractAbiEvent extends CompilerOutputContractAbi {
        type: "event";
        anonymous: boolean;
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
    interface CompilerOutputSources {
        [globalName: string]: {
            id: number;
            ast: any;
            legacyAST: any;
        },
    }
    interface CompilerOutputContracts {
        [globalName: string]: {
            abi: (CompilerOutputContractAbiFunction|CompilerOutputContractAbiEvent)[];
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
    }
    interface CompilerOutput {
        errors?: CompilerOutputError[];
        sources: CompilerOutputSources;
        contracts: CompilerOutputContracts;
    }
    type ReadCallback = (path: string) => { contents?: string, error?: string};
    function compileStandardWrapper(input: string, readCallback?: ReadCallback);
}
