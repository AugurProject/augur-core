import { expect } from "chai";
import { compileAndDeployContracts } from "../deployment/deployContracts";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { stringTo32ByteHex } from "../libraries/HelperFunctions";
import { Connector } from '../libraries/Connector';
import { Configuration } from '../libraries/Configuration';

describe("Universe", () => {
    var contractDeployer: ContractDeployer;
    beforeEach(async () => {
        const configuration = await Configuration.create();
        const connector = new Connector(configuration);
        contractDeployer = await compileAndDeployContracts(configuration, connector);
    });
    it("#getTypeName()", async () => {
        // TODO: Move this check into ContractDeployer
        const genesisUniverse = contractDeployer.universe;;
        const genesisUniverseTypeNameHex = await genesisUniverse.getTypeName_();
        const genesisUniverseTypeName = stringTo32ByteHex(genesisUniverseTypeNameHex);
        expect(genesisUniverseTypeName).to.equal("Universe");
    });
});
