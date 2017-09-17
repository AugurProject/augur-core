#!/usr/bin/env node

import * as fs from 'fs';
import * as mkdirp from 'mkdirp';
import * as path from 'path';
import * as recursiveReadDir from 'recursive-readdir';
import { CompilerInput, CompilerInputSourceCode, CompilerInputSourceFile, compileStandardWrapper } from 'solc';

class SolidityContractCompiler {
    private contractInputDirectoryPath: string;
    private contractOutputDirectoryPath: string;
    private contractOutputFileName: string;

    public constructor(contractInputDirectoryPath: string, contractOutputDirectoryPath: string, contractOutputFileName: string) {
        this.contractInputDirectoryPath = contractInputDirectoryPath;
        this.contractOutputDirectoryPath = contractOutputDirectoryPath;
        this.contractOutputFileName = contractOutputFileName;
    }

    public async compileContracts() {
        try {
            // Compile all contracts in this.inputDirectoryPath
            const inputJson: CompilerInput = await this.generateCompilerInput();
            console.log(inputJson);
            console.log('---------');
            const compilerOutput: any = compileStandardWrapper(JSON.stringify(inputJson), this.readCallback);
            console.log(compilerOutput);
            // if (compilerOutput.errors.length > 0) {
            //     // TODO: Improve error handling
            //     console.error("The compiler encountered the following warnings/errors:");
            //     for (let error of compilerOutput.errors) {
            //         console.error(error);
            //     }
            // }

            // // Create output directory (if it doesn't exist) and save contract bytecodes to single file
            // mkdirp(this.contractOutputDirectoryPath);
            // const contractOutputFilePath = this.contractOutputDirectoryPath + "/" + this.contractOutputFileName;
            // let wstream: any = fs.createWriteStream(contractOutputFilePath);
            // for (let contract in compilerOutput.contracts) {
            //     wstream.write(compilerOutput.contracts[contract].bytecode);
            // }

            // console.log("Saved " + contractOutputFilePath);
        } catch (error) {
            console.error(error);
        }
    }

    public readCallback(path: string): { content?: string, error?: string } {
        try {
            const result = fs.readFileSync(path, 'utf8');
            return { content: result };
        } catch (error) {
            console.log(error)
            return { error: error.message };
        }
    }

    private ignoreFunc(file: string, stats: fs.Stats): boolean {
        return stats.isFile() && path.extname(file) != ".sol";
    }

    private async generateCompilerInput(): Promise<CompilerInput> {
        var inputJson: CompilerInput = {
            "language": "Solidity",
            "sources": {}
        };
        try {
            let contractInputDirectoryPath = this.contractInputDirectoryPath;
            if (contractInputDirectoryPath.lastIndexOf(path.sep) != contractInputDirectoryPath.length) {
                contractInputDirectoryPath += path.sep;
            }

            const files: any = await recursiveReadDir(this.contractInputDirectoryPath, [this.ignoreFunc]);
            for (let index in files) {
                inputJson.sources[files[index].replace(contractInputDirectoryPath, "")] = {"urls": [files[index]]};
            }
        } catch (error) {
            console.error(error);
        }
        return inputJson;
    }
}


const inputDirectoryPath = path.join(__dirname, "../../source/contracts");
const outputDirectoryPath = path.join(__dirname, "../contracts");
const outputFileName = "augurCore";

const solidityContractCompiler = new SolidityContractCompiler(inputDirectoryPath, outputDirectoryPath, outputFileName);
console.log(solidityContractCompiler.readCallback('/Users/aaron/Documents/Augur/augur-core/source/contracts/Apple.sol'));
//solidityContractCompiler.compileContracts();
