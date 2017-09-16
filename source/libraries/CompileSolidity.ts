#!/usr/bin/env node

import * as fs from 'fs';
import * as mkdirp from 'mkdirp';
import * as path from 'path';
import * as recursiveReadDir from 'recursive-readdir';
import * as solc from 'solc';

class SolidityContractCompiler {
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
        const inputJson: any = this.generateCompilerInput();
        const compilerOutput: any = solc.compileStandardWrapper(inputJson);
        // console.log(compilerOutput);
        if (compilerOutput.errors.length > 0) {
            // TODO: Improve error handling
            console.error("The compiler encountered the following warnings/errors:");
            for (let error of compilerOutput.errors) {
                console.error(error);
            }
        }

        // Create output directory (if it doesn't exist) and save contract bytecodes to single file
        mkdirp(this.contractOutputDirectoryPath);
        const contractOutputFilePath = this.contractOutputDirectoryPath + "/" + this.contractOutputFileName;
        let wstream: any = fs.createWriteStream(contractOutputFilePath);
        for (let contract in compilerOutput.contracts) {
            wstream.write(compilerOutput.contracts[contract].bytecode);
        }

        console.log("Saved " + contractOutputFilePath);
    }

    private async generateCompilerInput() {
        try {
            const files = await recursiveReadDir(this.contractInputDirectoryPath);
            let inputJson: any = {
                language: "Solidity",
                sources: {}
            };
            for (let filePath of files) {
                let stat: any = fs.lstatSync(filePath);
                if (stat.isFile() && path.extname(filePath) == '.sol') {
                    inputJson.sources[filePath] = fs.readFileSync(filePath, 'utf8');
                }
            }
            return inputJson;
        } catch (error) {
            console.error(error);
        }
    }
}


const inputDirectoryPath = path.join(__dirname, "../contracts");
const outputDirectoryPath = path.join(__dirname, "../../output/contracts");
const outputFileName = "augurCore";

const solidityContractCompiler = new SolidityContractCompiler(inputDirectoryPath, outputDirectoryPath, outputFileName);
solidityContractCompiler.compileContracts();
