import * as binascii from 'binascii';
import { expect } from "chai";
import { ContractBlockchainData } from "contract-deployment";
import { compileAndDeployContracts } from "../deployment/deployContracts";


describe('Branch', () => {
    let contracts: ContractBlockchainData[] = [];
    beforeEach(async () => {
        contracts = await compileAndDeployContracts();
    });
    it('#assertIsWhitelisted()', async () => {
        const contractTypeNameHex = (await contracts['Branch']["Branch"].getTypeName())[0];
        const contractTypeName = binascii.unhexlify(contractTypeNameHex).replace(/\u0000/g, '');
        expect(contractTypeName).to.equal("Branch");
    });
});
