#!/usr/bin/env node

import * as fs from 'fs';
import * as readFile from 'fs-readfile-promise';
import * as mkdirp from 'mkdirp';
import * as path from 'path';
import * as recursiveReadDir from 'recursive-readdir';
import { CompilerInput, CompilerOutput, compileStandardWrapper } from 'solc';

interface CompileContractsOutput {
    output?: string;
}

export class SolidityContractCompiler {
    private contractInputDirectoryPath: string;
    private contractOutputDirectoryPath: string;
    private contractOutputFileName: string;

    public constructor(contractInputDirectoryPath: string, contractOutputDirectoryPath: string, contractOutputFileName: string) {
        if (contractInputDirectoryPath.lastIndexOf(path.sep) != contractInputDirectoryPath.length - 1) {
            contractInputDirectoryPath += path.sep;
        }
        if (contractOutputDirectoryPath.lastIndexOf(path.sep) != contractOutputDirectoryPath.length - 1) {
            contractOutputDirectoryPath += path.sep;
        }
        this.contractInputDirectoryPath = contractInputDirectoryPath;
        this.contractOutputDirectoryPath = contractOutputDirectoryPath;
        this.contractOutputFileName = contractOutputFileName;
    }

    public readCallback(path: string): { contents?: string, error?: string } {
        try {
            const result = fs.readFileSync(path, 'utf8');
            return { contents: result };
        } catch (error) {
            return { error: error.message };
        }
    }

    public async compileContracts(): Promise<CompileContractsOutput> {
        // Check if all contracts are cached (and thus do not need to be compiled)
        try {
            const stats = fs.statSync(this.contractOutputDirectoryPath + this.contractOutputFileName);
            const lastCompiledTimestamp = stats.mtime;
            const uncachedFiles = await recursiveReadDir(this.contractInputDirectoryPath, [function(file: string, stats: fs.Stats): boolean {return stats.isDirectory() || (stats.isFile() && path.extname(file) != ".sol") || (stats.isFile() && path.extname(file) == ".sol" && stats.mtime < lastCompiledTimestamp);}]);
            if (uncachedFiles.length == 0) {
                return { output: "Contracts in " + this.contractInputDirectoryPath + " have not been modified since last cache was created" };
            }
        } catch (error) {
            // Unable to read compiled contracts output file (likely because it has not been generated)
        }

        // Compile all contracts in the specified input directory
        const compilerInputJson = await this.generateCompilerInput();
        const compilerOutputJson: string = compileStandardWrapper(JSON.stringify(compilerInputJson), this.readCallback);
        const compilerOutput: CompilerOutput = JSON.parse(compilerOutputJson);
        if (compilerOutput.errors) {
            let errors = "";
            for (let error of compilerOutput.errors) {
                errors += error.formattedMessage + "\n";
            }
            throw new Error("The following errors/warnings were returned by solc:\n\n" + errors);
        }

        // Create output directory (if it doesn't exist)
        mkdirp(this.contractOutputDirectoryPath, this.mkdirpCallback);

        // Output contract data to single file
        const contractOutputFilePath = this.contractOutputDirectoryPath + this.contractOutputFileName;
        let wstream: any = fs.createWriteStream(contractOutputFilePath);
        wstream.write(JSON.stringify(compilerOutput.contracts));

        return { output: "Contracts in " + this.contractInputDirectoryPath + " were successfully compiled by solc and saved to " + contractOutputFilePath};
    }

    private ignoreFile(file: string, stats: fs.Stats): boolean {
        return !stats.isDirectory() && path.extname(file) != ".sol";
    }

    private mkdirpCallback(error): void {
        if (error) {
            throw new Error (error);
        }
    }

    private async generateCompilerInput(): Promise<CompilerInput> {
        const filePaths: any = await recursiveReadDir(this.contractInputDirectoryPath, [this.ignoreFile]);
        const filesPromises = filePaths.map(async filePath => await readFile(filePath));
        const files = await Promise.all(filesPromises);

        let inputJson: CompilerInput = {
            language: "Solidity",
            settings: {
                outputSelection: {
                    "*": {
                        "*": [ "abi", "evm.bytecode.object" ]
                    }
                }
            },
            sources: {}
        };
        for (var file in files) {
            const filePath = filePaths[file].replace(this.contractInputDirectoryPath, "").replace(/\\/g, "/");
            inputJson.sources[filePath] = { content : files[file].toString() };
        }

        return inputJson;
    }
}
