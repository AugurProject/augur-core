import * as fs from "async-file";
import readFile = require('fs-readfile-promise');
import * as path from "path";
import * as recursiveReadDir from "recursive-readdir";
import asyncMkdirp = require('async-mkdirp');
import { CompilerInput, CompilerOutput, CompilerOutputEvmBytecode } from "solc";
import { Abi } from "ethereum";
import { ChildProcess, exec, spawn } from "child_process";
import { format } from "util";
import { CompilerConfiguration } from './CompilerConfiguration';

interface AbiOutput {
    [contract: string]: Abi;
}

export class ContractCompiler {
    private readonly configuration: CompilerConfiguration;
    private readonly flattenerBin = "solidity_flattener";
    private readonly flattenerCommand: string;


    public constructor(configuration: CompilerConfiguration) {
        this.configuration = configuration;
        this.flattenerCommand = `${this.flattenerBin} --allow-path . %s`;
    }

    private async getCommandOutputFromInput(childProcess: ChildProcess, stdin: string): Promise<string> {
        return new Promise<string>((resolve, reject) => {
            const buffers: Array<Buffer> = [];
            childProcess.stdout.on('data', function (data: Buffer) {
                buffers.push(data);
            });
            const errorBuffers: Array<Buffer> = [];
            childProcess.stderr.on('data', function (data: Buffer) {
                errorBuffers.push(data);
            });
            childProcess.on('close', function (code) {
                const errorMessage = Buffer.concat(errorBuffers).toString();
                if (code > 0) return reject(new Error(`Process Exit Code ${code}\n${errorMessage}`))
                return resolve(Buffer.concat(buffers).toString());
            });
            childProcess.stdin.write(stdin);
            childProcess.stdin.end();
        })
    }

    // TODO: Use solcjs compileStandardWrapper when it works, 0.4.24 giving error: "Runtime.functionPointers[index] is not a function"
    private async compileCustomWrapper(compilerInputJson: CompilerInput): Promise<CompilerOutput> {
        const childProcess = spawn("solc", ["--standard-json"]);
        const compilerOutputJson = await this.getCommandOutputFromInput(childProcess, JSON.stringify(compilerInputJson));
        return JSON.parse(compilerOutputJson);
    }

    public async compileContracts(): Promise<CompilerOutput> {
        // Check if all contracts are cached (and thus do not need to be compiled)
        try {
            if (!this.configuration.enableSdb) {
                const stats = await fs.stat(this.configuration.contractOutputPath);
                const lastCompiledTimestamp = stats.mtime;
                const ignoreCachedFile = function (file: string, stats: fs.Stats): boolean {
                    return (stats.isFile() && path.extname(file) !== ".sol") || (stats.isFile() && path.extname(file) === ".sol" && stats.mtime < lastCompiledTimestamp);
                }
                const uncachedFiles = await recursiveReadDir(this.configuration.contractSourceRoot, [ignoreCachedFile]);
                if (uncachedFiles.length === 0) {
                    return JSON.parse(await fs.readFile(this.configuration.contractOutputPath, "utf8"));
                }
            }
        } catch {
            // Unable to read compiled contracts output file (likely because it has not been generated)
        }

        console.log('Compiling contracts, this may take a minute...');

        // Compile all contracts in the specified input directory
        const compilerInputJson = await this.generateCompilerInput();
        const compilerOutput = await this.compileCustomWrapper(compilerInputJson);

        if (compilerOutput.errors) {
            let errors = "";

            for (let error of compilerOutput.errors) {
                // FIXME: https://github.com/ethereum/solidity/issues/3273
                if (error.message.includes("instruction is only available after the Metropolis hard fork")) continue;
                errors += error.formattedMessage + "\n";
            }

            if (errors.length > 0) {
                throw new Error("The following errors/warnings were returned by solc:\n\n" + errors);
            }
        }

        // Create output directory (if it doesn't exist)
        await asyncMkdirp(path.dirname(this.configuration.contractOutputPath));

        // Output contract data to single file
        const filteredCompilerOutput = this.filterCompilerOutput(compilerOutput);
        await fs.writeFile(this.configuration.contractOutputPath, JSON.stringify(filteredCompilerOutput, null, '\t'));

        // Output abi data to a single file
        const abiOutput = this.generateAbiOutput(filteredCompilerOutput);
        await fs.writeFile(this.configuration.abiOutputPath, JSON.stringify(abiOutput, null, '\t'));

        return filteredCompilerOutput;
    }

    public async generateFlattenedSolidity(filePath: string): Promise<string> {
        const relativeFilePath = filePath.replace(this.configuration.contractSourceRoot, "").replace(/\\/g, "/");

        const childProcess = exec(format(this.flattenerCommand, relativeFilePath), {
            encoding: "buffer",
            cwd: this.configuration.contractSourceRoot
        });
        return await this.getCommandOutputFromInput(childProcess, "");
    }

    public async generateCompilerInput(): Promise<CompilerInput> {
        const ignoreFile = function(file: string, stats: fs.Stats): boolean {
            return file.indexOf("legacy_reputation") > -1 || (stats.isFile() && path.extname(file) !== ".sol");
        }
        const filePaths = await recursiveReadDir(this.configuration.contractSourceRoot, [ignoreFile]);
        let filesPromises;
        if (this.configuration.useFlattener) {
            filesPromises = filePaths.map(async filePath => (await this.generateFlattenedSolidity(filePath)));
        } else {
            filesPromises = filePaths.map(async filePath => (await readFile(filePath)).toString('utf8'));
        }
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
        if (this.configuration.enableSdb) {
            inputJson.settings.optimizer = {
                enabled: false
            }
            inputJson.settings.outputSelection["*"][""] = [ "legacyAST" ];
            inputJson.settings.outputSelection["*"]["*"].push("evm.bytecode.sourceMap");
            inputJson.settings.outputSelection["*"]["*"].push("evm.deployedBytecode.object");
            inputJson.settings.outputSelection["*"]["*"].push("evm.deployedBytecode.sourceMap");
            inputJson.settings.outputSelection["*"]["*"].push("evm.methodIdentifiers");
        }
        for (var file in files) {
            const filePath = filePaths[file].replace(this.configuration.contractSourceRoot, "").replace(/\\/g, "/").replace(/^\//, "");;
            inputJson.sources[filePath] = { content : files[file] };
        }

        return inputJson;
    }

    private filterCompilerOutput(compilerOutput: CompilerOutput): CompilerOutput {
        const result: CompilerOutput = { contracts: {} };
        for (let relativeFilePath in compilerOutput.contracts) {
            for (let contractName in compilerOutput.contracts[relativeFilePath]) {
                // don't include libraries
                if (relativeFilePath.startsWith('libraries/') && contractName !== 'Delegator' && contractName !== 'Map') continue;
                // don't include embedded libraries
                if (!(relativeFilePath === `${contractName}.sol` || relativeFilePath.endsWith(`/${contractName}.sol`))) continue;
                const contract = compilerOutput.contracts[relativeFilePath][contractName];
                const abi = contract.abi;
                if (abi === undefined) continue;
                const bytecode = contract.evm.bytecode;
                if (bytecode.object === undefined) continue;
                // don't include interfaces or Abstract contracts
                if (/^(?:I|Base|DS)[A-Z].*/.test(contractName)) continue;
                if (bytecode.object.length === 0) throw new Error("Contract: " + contractName + " has no bytecode, but this is not expected. It probably doesn't implement all its abstract methods");

                result.contracts[relativeFilePath] = {
                    [contractName]: {
                        abi: abi,
                        evm: { bytecode: { object: bytecode.object } }
                    }
                }

                if (this.configuration.enableSdb) {
                    const deployedBytecode = contract.evm.deployedBytecode;
                    if (deployedBytecode === undefined || deployedBytecode.object === undefined || deployedBytecode.sourceMap === undefined) continue;
                    if (bytecode.sourceMap === undefined) continue;
                    const methodIdentifiers = contract.evm.methodIdentifiers;
                    if (methodIdentifiers === undefined) continue;
                    result.contracts[relativeFilePath][contractName].evm.bytecode.sourceMap = bytecode.sourceMap;
                    result.contracts[relativeFilePath][contractName].evm.deployedBytecode = <CompilerOutputEvmBytecode> {
                        object: deployedBytecode.object,
                        sourceMap: deployedBytecode.sourceMap
                    };
                    result.contracts[relativeFilePath][contractName].evm.methodIdentifiers = JSON.parse(JSON.stringify(methodIdentifiers));
                }
            }
        }

        if (this.configuration.enableSdb && compilerOutput.sources !== undefined) {
            result.sources = {};
            for (let relativeFilePath in compilerOutput.sources) {
                if (relativeFilePath in result.contracts) {
                    // only legacyAST is used, but including ast to be compliant with interface
                    result.sources[relativeFilePath] = {
                        id: compilerOutput.sources[relativeFilePath].id,
                        ast: JSON.parse(JSON.stringify(compilerOutput.sources[relativeFilePath].legacyAST)),
                        legacyAST: JSON.parse(JSON.stringify(compilerOutput.sources[relativeFilePath].legacyAST))
                    }
                }
            }
        }

        return result;
    }

    private generateAbiOutput(compilerOutput: CompilerOutput): AbiOutput {
        const result: AbiOutput = {};
        for (let relativeFilePath in compilerOutput.contracts) {
            for (let contractName in compilerOutput.contracts[relativeFilePath]) {
                result[contractName] = compilerOutput.contracts[relativeFilePath][contractName].abi;
            }
        }

        return result;
    }
}
