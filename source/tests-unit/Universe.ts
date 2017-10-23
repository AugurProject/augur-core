import * as binascii from "binascii";
import { expect } from "chai";
import { compileAndDeployContracts } from "../deployment/deployContracts";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { parseAbiIntoMethods } from "../libraries/AbiParser";
import { stringTo32ByteHex } from "../libraries/HelperFunctions";


describe("Universe", () => {
    var contractDeployer: ContractDeployer;
    beforeEach(async () => {
        contractDeployer = await compileAndDeployContracts();
    });
    it("#getTypeName()", async () => {
        // TODO: Move this check into ContractDeployer
        const genesisUniverse = parseAbiIntoMethods(contractDeployer.ethjsQuery, contractDeployer.abis.get('Universe')!, { from: contractDeployer.testAccounts[0], to: contractDeployer.universeAddress, gasPrice: contractDeployer.gasPrice });
        const genesisUniverseTypeNameHex = (await genesisUniverse.getTypeName())[0];
        const genesisUniverseTypeName = stringTo32ByteHex(genesisUniverseTypeNameHex);
        expect(genesisUniverseTypeName).to.equal("Universe");
    });
});
