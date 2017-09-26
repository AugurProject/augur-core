import * as binascii from 'binascii';
import * as path from 'path';
import { expect } from 'chai';
import { ContractBlockchainData } from 'contract-deployment';
import { compileAndDeployContracts } from "../deployment/deployContracts";


describe('Apple', () => {
    let contracts: ContractBlockchainData[] = [];
    beforeEach(async () => {
        // TODO: Prevent this from timing out by using a "done" function
        const contractInputDirectoryPath = path.join(__dirname, "../../source/contracts");
        const contractOutputDirectoryPath = path.join(__dirname, "../contracts");
        const contractOutputFileName = "augurCore";
        const httpProviderport = 8545;
        const gas = 3000000;

        contracts = await compileAndDeployContracts(contractInputDirectoryPath, contractOutputDirectoryPath, contractOutputFileName, httpProviderport, gas);
    });
    it('#getTypeName()', async () => {
        const contractTypeNameHex = (await contracts['Apple.sol']["Apple"].getTypeName())[0];
        const contractTypeName = binascii.unhexlify(contractTypeNameHex).replace(/\u0000/g, '');
        expect(contractTypeName).to.equal("Apple");
    });
});
