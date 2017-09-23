import * as binascii from 'binascii';
import * as fs from 'async-file';
import * as path from 'path';
import * as HttpProvider from 'ethjs-provider-http';
import * as Eth from 'ethjs-query';
import * as EthContract from 'ethjs-contract';
import { SolidityContractCompiler } from "../libraries/CompileSolidity";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { RpcClient } from "../libraries/RpcClient";
import { expect } from 'chai';


describe('Apple', () => {
    describe('#getTypeName()', function() {
        it('unable to get contract type name', async function() {
            try {
                // TODO: Find a better way to prevent test from timing out (probably using done)
                this.timeout(5000);

                // Compile contracts to a single output file
                const contractInputDirectoryPath = path.join(__dirname, "../../source/contracts");
                const contractOutputDirectoryPath = path.join(__dirname, "../contracts");
                const contractOutputFileName = "augurCore";

                const solidityContractCompiler = new SolidityContractCompiler(contractInputDirectoryPath, contractOutputDirectoryPath, contractOutputFileName);
                const compilerResult = await solidityContractCompiler.compileContracts();

                // Initialize RPC client
                const port = 8545;
                const rpcClient = new RpcClient();
                await rpcClient.listen(port);

                // Initialize Eth object
                const httpProviderUrl = "http://localhost:" + port;
                const eth = new Eth(new HttpProvider(httpProviderUrl));
                const accounts = await eth.accounts();
                const fromAccount = accounts[0];

                // Read in contract ABIs and bytecodes as JSON string
                const contractJson = await fs.readFile(contractOutputDirectoryPath + "/" + contractOutputFileName, "utf8");
                const gas = 3000000;

                // Deploy contracts to blockchain
                const contractDeployer = new ContractDeployer();
                const contracts = await contractDeployer.deployContracts(eth, contractJson, fromAccount, gas);

                // Test Apple's getTypeName() function
                const contractTypeNameHex = (await contracts["Apple"].getTypeName())[0];
                const contractTypeName = binascii.unhexlify(contractTypeNameHex).replace(/\u0000/g, '');
                expect(contractTypeName).to.equal("Apple");
            } catch (error) {
                throw error;
            }
        });
    });
});
