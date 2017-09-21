#!/usr/bin/env node

import * as fs from 'fs';
import * as readFile from 'fs-readfile-promise';
import * as mkdirp from 'mkdirp';
import * as path from 'path';
import * as recursiveReadDir from 'recursive-readdir';
import { CompilerInput, CompilerInputSourceCode, CompilerInputSourceFile, CompilerOutput, CompilerOutputError, CompilerOutputContractAbi, CompilerOutputEvmBytecode, compileStandardWrapper } from 'solc';

interface CompileContractsOutput {
    output?: string;
}

class SolidityContractCompiler {
    private contractInputDirectoryPath: string;
    private contractOutputDirectoryPath: string;
    private contractOutputFileName: string;

    public constructor(contractInputDirectoryPath: string, contractOutputDirectoryPath: string, contractOutputFileName: string) {
        this.contractInputDirectoryPath = contractInputDirectoryPath;
        this.contractOutputDirectoryPath = contractOutputDirectoryPath;
        this.contractOutputFileName = contractOutputFileName;
    }

    public async compileContracts(): Promise<CompileContractsOutput> {
        try {
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
            const contractOutputFilePath = this.contractOutputDirectoryPath + "/" + this.contractOutputFileName;
            let wstream: any = fs.createWriteStream(contractOutputFilePath);
            for (let contract in compilerOutput.contracts) {
                wstream.write(JSON.stringify(compilerOutput.contracts[contract]));
            }

            return { output: "Contracts in " + this.contractInputDirectoryPath + " were successfully compiled by solc and saved to " + contractOutputFilePath};
        } catch (error) {
            throw error;
        }
    }

    private ignoreFile(file: string, stats: fs.Stats): boolean {
        return stats.isFile() && path.extname(file) != ".sol";
    }

    public readCallback(path: string): { contents?: string, error?: string } {
        try {
            const result = fs.readFileSync(path, 'utf8');
            return { contents: result };
        } catch (error) {
            return { error: error.message };
        }
    }

    private mkdirpCallback(error): void {
        if (error) {
            throw new Error (error);
        }
    }

    private async generateCompilerInput(): Promise<CompilerInput> {
        let inputJson: CompilerInput = {
            "language": "Solidity",
            "sources": {}
        };
        try {
            let contractInputDirectoryPath = this.contractInputDirectoryPath;
            if (contractInputDirectoryPath.lastIndexOf(path.sep) != contractInputDirectoryPath.length) {
                contractInputDirectoryPath += path.sep;
            }

            const filePaths: any = await recursiveReadDir(this.contractInputDirectoryPath, [this.ignoreFile]);
            const filesPromises = filePaths.map(async filePath => await readFile(filePath));
            const files = await Promise.all(filesPromises);

            for (var file in files) {
                inputJson.sources[filePaths[file].replace(contractInputDirectoryPath, "")] = { content : files[file].toString() };
            }
        } catch (error) {
            throw error;
        }
        return inputJson;
    }
}
