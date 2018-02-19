declare module 'solc' {
    import { Abi, Primitive } from 'ethereum';

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
    interface CompilerOutputEvmBytecode {
        object: string;
        opcodes?: string;
        sourceMap?: string;
        linkReferences?: {} | {
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
            [contractName: string]: {
                abi: Abi;
                metadata?: string;
                userdoc?: any;
                devdoc?: any;
                ir?: string;
                evm: {
                    assembly?: string;
                    legacyAssembly?: any;
                    bytecode: CompilerOutputEvmBytecode;
                    deployedBytecode?: CompilerOutputEvmBytecode;
                    methodIdentifiers?: {
                        [methodName: string]: string;
                    };
                    gasEstimates?: {
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
                ewasm?: {
                    wast: string;
                    wasm: string;
                }
            }
        };
    }
    interface CompilerOutput {
        errors?: CompilerOutputError[];
        sources?: CompilerOutputSources;
        contracts: CompilerOutputContracts;
    }
    type ReadCallback = (path: string) => { contents?: string, error?: string};
    function compileStandardWrapper(input: string, readCallback?: ReadCallback): string;
}
