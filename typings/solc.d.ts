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
            [globalName: string]: CompilerInputSourceFile,
        };
    }
    function compileStandardWrapper(input: string, readCallback?: any);
}
