import * as binascii from "binascii";
import { expect } from "chai";
import { compileAndDeployContracts } from "../deployment/deployContracts";
import { ContractDeployer } from "../libraries/ContractDeployer";


describe("Universe", () => {
    var contractDeployer: ContractDeployer;
    beforeEach(async () => {
        contractDeployer = await compileAndDeployContracts();
    });
    it("#getTypeName()", async () => {
        const contracts = contractDeployer.getContracts();
        const contractTypeNameHex = (await contracts["Universe"].getTypeName())[0];
        const contractTypeName = binascii.unhexlify(contractTypeNameHex).replace(/\u0000/g, "");
        expect(contractTypeName).to.equal("Universe");

        const universe = contractDeployer.getUniverse();
        const universeTypeName = await universe.getTypeName();
        expect(universeTypeName).to.equal("Universe");
    });
});
