#!/usr/bin/env node

import * as fs from 'fs';
import * as path from 'path';
import * as solc from 'solc';

class SolidityContractCompiler {
    private compiler: any = solc;
    private contractInputDirectoryPath: string;
    private contractOutputDirectoryPath: string;
    private contractOutputFileName: string;

    public constructor(contractInputDirectoryPath: string, contractOutputDirectoryPath: string, contractOutputFileName: string) {
        this.contractInputDirectoryPath = contractInputDirectoryPath;
        this.contractOutputDirectoryPath = contractOutputDirectoryPath;
        this.contractOutputFileName = contractOutputFileName;
    }

    public compileContracts() {
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

    private getContractFilePaths(directoryPath){
        let contractFilePaths: string[] = [];
        if (!fs.existsSync(directoryPath)) {
            console.log("Invalid directory path: ", directoryPath);
        } else {
            let filesInCurrentDirectory: any = fs.readdirSync(directoryPath);
            for (let file of filesInCurrentDirectory) {
                let filePath: string = path.join(directoryPath, file);
                let stat: any = fs.lstatSync(filePath);
                if (stat.isDirectory()) {
                    let filePaths: string[] = this.getContractFilePaths(filePath);
                    for (let filePath of filePaths) {
                        contractFilePaths.push(filePath);
                    }
                } else if (stat.isFile() && filePath.split(".").pop() == "sol") {
                    contractFilePaths.push(filePath);
                }
            }
        }

        return contractFilePaths;
    }

    private generateCompilerInput() {
        let inputJSON: any = {
            language: "Solidity",
            sources: {}
        };
        let filePaths: string[] = this.getContractFilePaths(this.contractInputDirectoryPath);
        for (let filePath of filePaths) {
            inputJSON.sources[filePath] = fs.readFileSync(filePath, 'utf8');
        }
        return inputJSON;
    }

    private createOutputDirectory() {
        let initDir: string = path.isAbsolute(this.contractOutputDirectoryPath) ? path.sep : '';
        this.contractOutputDirectoryPath.split(path.sep).reduce((parentDir, childDir) => {
            let curDir: string = path.resolve(parentDir, childDir);
            if (!fs.existsSync(curDir)) {
                fs.mkdirSync(curDir);
            }

            return curDir;
        }, initDir);
    }
}
