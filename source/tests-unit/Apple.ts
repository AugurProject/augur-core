import * as binascii from 'binascii';
import * as fs from 'async-file';
import * as path from 'path';
import * as HttpProvider from 'ethjs-provider-http';
import * as Eth from 'ethjs-query';
import * as EthContract from 'ethjs-contract';
import { expect } from 'chai';
import { ContractBlockchainData } from 'contract-deployment';
import { SolidityContractCompiler } from "../libraries/CompileSolidity";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { RpcClient } from "../libraries/RpcClient";
import { compileAndDeployContracts } from "../deployment/deployContracts";


describe('Apple', () => {
    beforeEach(async function(done) {
        // TODO: Figure out how to prevent this from timing out by using a "done" function
        const contractInputDirectoryPath = path.join(__dirname, "../../source/contracts");
        const contractOutputDirectoryPath = path.join(__dirname, "../contracts");
        const contractOutputFileName = "augurCore";
        const httpProviderport = 8545;
        const gas = 3000000;

        return await compileAndDeployContracts(contractInputDirectoryPath, contractOutputDirectoryPath, contractOutputFileName, httpProviderport, gas);
    });
    describe('#getTypeName()', function() {
        it('unable to get contract type name', async function() {
            // Test Apple's getTypeName() function
            const contractTypeNameHex = (await contracts["Apple"].getTypeName())[0];
            const contractTypeName = binascii.unhexlify(contractTypeNameHex).replace(/\u0000/g, '');
            expect(contractTypeName).to.equal("Apple");
        });
    });
});
