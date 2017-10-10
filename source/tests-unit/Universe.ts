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
        // TODO: Move this check into ContractDeployer
        const genesisUniverse = await contractDeployer.getUniverse();
        const genesisUniverseTypeNameHex = (await genesisUniverse.getTypeName())[0];
        const genesisUniverseTypeName = binascii.unhexlify(genesisUniverseTypeNameHex).replace(/\u0000/g, "");
        expect(genesisUniverseTypeName).to.equal("Universe");
    });
});
