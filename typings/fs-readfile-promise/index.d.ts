declare module 'fs-readfile-promise' {
    function readFile(path: string): Promise<Buffer>;
    export = readFile;
}
