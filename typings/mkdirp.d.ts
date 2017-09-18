import * as fs from "fs";
declare namespace MkDirp {
    interface mkdirp {
        (path: string): Promise<string[]>;
    }
}

declare var mkdirp: MkDirp.mkdirp;
export = mkdirp;
