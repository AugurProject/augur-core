declare namespace ReadFilePromise {
    interface readFile {
        (path: string): Promise<string[]>;
    }
}

declare var ReadFilePromise: ReadFilePromise.readFile;
export = ReadFilePromise;
