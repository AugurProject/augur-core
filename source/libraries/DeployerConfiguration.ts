import * as path from 'path';

export class DeployerConfiguration {
    public readonly contractInputPath: string;
    public readonly contractAddressesOutputPath: string;
    public readonly uploadBlockNumbersOutputPath: string;
    public readonly controllerAddress: string|undefined;
    public readonly createGenesisUniverse: boolean;
    public readonly useNormalTime: boolean;

    public constructor(contractInputRoot: string, artifactOutputRoot: string, controllerAddress: string|undefined, createGenesisUniverse: boolean=true, isProduction: boolean=false, useNormalTime: boolean=true) {
        this.controllerAddress = controllerAddress;
        this.createGenesisUniverse = createGenesisUniverse;
        this.useNormalTime = isProduction || useNormalTime;

        this.contractAddressesOutputPath = path.join(artifactOutputRoot, 'addresses.json');
        this.uploadBlockNumbersOutputPath = path.join(artifactOutputRoot, 'upload-block-numbers.json');
        this.contractInputPath = path.join(contractInputRoot, 'addresses.json');
    }

    public static create(isProduction: boolean=false): DeployerConfiguration {
        const contractInputRoot = (typeof process.env.CONTRACT_INPUT_ROOT === 'undefined') ? path.join(__dirname, '../../output/contracts') : path.normalize(<string> process.env.CONTRACT_INPUT_ROOT);
        const artifactOutputRoot = (typeof process.env.ARTIFACT_OUTPUT_ROOT === 'undefined') ? path.join(__dirname, '../../output/contracts') : path.normalize(<string> process.env.ARTIFACT_OUTPUT_ROOT);
        const controllerAddress = process.env.AUGUR_CONTROLLER_ADDRESS;
        const createGenesisUniverse = (typeof process.env.CREATE_GENESIS_UNIVERSE === 'undefined') ? true : process.env.CREATE_GENESIS_UNIVERSE === 'true';
        const useNormalTime = (typeof process.env.USE_NORMAL_TIME === 'string') ? process.env.USE_NORMAL_TIME === 'true' : true;

        return new DeployerConfiguration(contractInputRoot, artifactOutputRoot, controllerAddress, createGenesisUniverse, isProduction, useNormalTime);
    }

}
