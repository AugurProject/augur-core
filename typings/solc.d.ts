declare module 'solc' {
    interface CompilerInputSourceFile {
        keccak256?: string;
        content: string;
    }
    interface CompilerInputSourceCode {
        keccak256?: string;
        content: string;
    }
    interface CompilerInput {
        language: "Solidity" | "serpent" | "lll" | "assembly";
        sources: {
            [globalName: string]: CompilerInputSourceFile,
        };
    }
    type ReadCallback = (path: string) => { contents?: string, error?: string};
    function compileStandardWrapper(input: string, readCallback?: ReadCallback);
}
