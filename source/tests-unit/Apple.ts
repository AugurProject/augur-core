import * as binascii from 'binascii';
import * as path from 'path';
import { expect } from 'chai';
import { ContractBlockchainData } from 'contract-deployment';
import { compileAndDeployContracts } from "../deployment/deployContracts";


describe('Apple', () => {
    let contracts: ContractBlockchainData[] = [];
    beforeEach(async () => {
        contracts = await compileAndDeployContracts();
    });
    it('#getTypeName()', async () => {
        const contractTypeNameHex = (await contracts['Apple.sol']["Apple"].getTypeName())[0];
        const contractTypeName = binascii.unhexlify(contractTypeNameHex).replace(/\u0000/g, '');
        expect(contractTypeName).to.equal("Apple");
    });
});
