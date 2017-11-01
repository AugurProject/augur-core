#!/usr/bin/env node

import * as fs from "async-file";
import * as readFile from "fs-readfile-promise";
import asyncMkdirp = require('async-mkdirp');
import * as path from "path";
import * as recursiveReadDir from "recursive-readdir";
import { CompilerInput, CompilerOutput, CompilerOutputContracts, compileStandardWrapper } from "solc";
import { Configuration } from './Configuration';

export class ContractCompiler {
    private readonly configuration: Configuration;

    public constructor(configuration: Configuration) {
        this.configuration = configuration
    }

    public async compileContracts(): Promise<CompilerOutputContracts> {
        // Check if all contracts are cached (and thus do not need to be compiled)
        try {
            const stats = await fs.stat(this.configuration.contractOutputPath);
            const lastCompiledTimestamp = stats.mtime;
            const ignoreCachedFile = function(file: string, stats: fs.Stats): boolean {
                return (stats.isFile() && path.extname(file) !== ".sol") || (stats.isFile() && path.extname(file) === ".sol" && stats.mtime < lastCompiledTimestamp);
            }
            const uncachedFiles = await recursiveReadDir(this.configuration.contractSourceRoot, [ignoreCachedFile]);
            if (uncachedFiles.length === 0) {
                return JSON.parse(await fs.readFile(this.configuration.contractOutputPath, "utf8"));
            }
        } catch {
            // Unable to read compiled contracts output file (likely because it has not been generated)
        }

        // Compile all contracts in the specified input directory
        const compilerInputJson = await this.generateCompilerInput();
        const compilerOutputJson = compileStandardWrapper(JSON.stringify(compilerInputJson));
        const compilerOutput: CompilerOutput = JSON.parse(compilerOutputJson);
        if (compilerOutput.errors) {
            let errors = "";
            for (let error of compilerOutput.errors) {
                errors += error.formattedMessage + "\n";
            }
            throw new Error("The following errors/warnings were returned by solc:\n\n" + errors);
        }

        // Create output directory (if it doesn't exist)
        await asyncMkdirp(path.dirname(this.configuration.contractOutputPath));

        // Output contract data to single file
        const contractOutputFilePath = this.configuration.contractOutputPath;
        await fs.writeFile(contractOutputFilePath, JSON.stringify(compilerOutput.contracts));

        return compilerOutput.contracts;
    }

    public async generateCompilerInput(): Promise<CompilerInput> {
        const ignoreFile = function(file: string, stats: fs.Stats): boolean {
            return file.indexOf("legacy_reputation") > -1 || (stats.isFile() && path.extname(file) !== ".sol");
        }
        const filePaths = await recursiveReadDir(this.configuration.contractSourceRoot, [ignoreFile]);
        const filesPromises = filePaths.map(async filePath => await readFile(filePath));
        const files = await Promise.all(filesPromises);

        let inputJson: CompilerInput = {
            language: "Solidity",
            settings: {
                optimizer: {
                    enabled: true,
                    runs: 500
                },
                outputSelection: {
                    "*": {
                        "*": [ "abi", "evm.bytecode.object" ]
                    }
                }
            },
            sources: {}
        };
        for (var file in files) {
            const filePath = filePaths[file].replace(this.configuration.contractSourceRoot, "").replace(/\\/g, "/");
            inputJson.sources[filePath] = { content : files[file].toString() };
        }

        return inputJson;
    }
}
