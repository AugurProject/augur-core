import * as fs from "fs";
declare namespace RecursiveReaddir {
    type IgnoreFunction = (file: string, stats: fs.Stats) => boolean;
    type Callback = (error: Error, files: string[]) => void;
    interface readDir {
        (path: string, ignores?: (string|IgnoreFunction)[]): Promise<string[]>;
        (path: string, callback: Callback): void;
        (path: string, ignores: (string|IgnoreFunction)[], callback: Callback): void;
    }
}

declare var recursiveReadDir: RecursiveReaddir.readDir;
export = recursiveReadDir;
