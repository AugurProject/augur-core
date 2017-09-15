#!/usr/bin/env node

import * as fs from 'fs';
import * as path from 'path';
import * as solc from 'solc';

class SolidityContractCompiler {
    contractLanguage: string;
    contractFileExtension: string;
    compiler: any;
    contractInputDirectoryPath: string;
    contractOutputDirectoryPath: string;
    contractOutputFileName: string;

    constructor(contractInputDirectoryPath: string, contractOutputDirectoryPath: string, contractOutputFileName: string) {
        this.contractLanguage = "Solidity";
        this.contractFileExtension = "sol";
        this.compiler = solc;
        this.contractInputDirectoryPath = contractInputDirectoryPath;
        this.contractOutputDirectoryPath = contractOutputDirectoryPath;
        this.contractOutputFileName = contractOutputFileName;
    }

    getContractFilePaths(directoryPath, contractFileExtension){
        let contractFilePaths: string[] = [];
        if (!fs.existsSync(directoryPath)) {
            console.log("Invalid directory path: ", directoryPath);
        } else {
            let filesInCurrentDirectory: any = fs.readdirSync(directoryPath);
            for (let file of filesInCurrentDirectory) {
                let filePath: string = path.join(directoryPath, file);
                let stat: any = fs.lstatSync(filePath);
                if (stat.isDirectory()) {
                    let filePaths: string[] = this.getContractFilePaths(filePath, contractFileExtension);
                    for (let filePath of filePaths) {
                        contractFilePaths.push(filePath);
                    }
                } else if (stat.isFile() && filePath.split(".").pop() == contractFileExtension) {
                    contractFilePaths.push(filePath);
                }
            }
        }

        return contractFilePaths;
    }

    generateCompilerInput() {
        let inputJSON: any = {
            language: this.contractLanguage,
            sources: {}
        };
        let filePaths: string[] = this.getContractFilePaths(this.contractInputDirectoryPath, this.contractFileExtension);
        for (let filePath of filePaths) {
            inputJSON.sources[filePath] = fs.readFileSync(filePath, 'utf8');
        }
        return inputJSON;
    }

    createOutputDirectory() {
        let initDir: string = path.isAbsolute(this.contractOutputDirectoryPath) ? path.sep : '';
        this.contractOutputDirectoryPath.split(path.sep).reduce((parentDir, childDir) => {
            let curDir: string = path.resolve(parentDir, childDir);
            if (!fs.existsSync(curDir)) {
                fs.mkdirSync(curDir);
            }

            return curDir;
        }, initDir);
    }

    compileContracts() {
        // Compile all contracts in this.inputDirectoryPath
        let inputJSON: any = this.generateCompilerInput();
        let compilerOutput: any = this.compiler.compile(inputJSON);
        if (compilerOutput.errors.length > 0) {
            console.log("The compiler encountered the following warnings/errors:");
            for (let error of compilerOutput.errors) {
                console.log(error);
            }
            // Do not return automatically in case there are only warnings and no errors
        }

        // Create output directory (if it doesn't exist) and save contract bytecodes to single file
        this.createOutputDirectory();
        let contractOutputFilePath: string = this.contractOutputDirectoryPath + "/" + this.contractOutputFileName;
        let wstream: any = fs.createWriteStream(contractOutputFilePath);
        for (let contract in compilerOutput.contracts) {
            wstream.write(compilerOutput.contracts[contract].bytecode);
        }

        console.log("Saved " + contractOutputFilePath);
    }
}
