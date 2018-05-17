import * as path from 'path';

const ARTIFACT_OUTPUT_ROOT  = (typeof process.env.ARTIFACT_OUTPUT_ROOT === 'undefined') ? path.join(__dirname, '../../output/contracts') : path.normalize(<string> process.env.ARTIFACT_OUTPUT_ROOT);

const PRODUCTION_LEGACY_REP_CONTRACT_ADDRESS = "0xe94327d07fc17907b4db788e5adf2ed424addff6";

export class DeployerConfiguration {
    public readonly contractInputPath: string;
    public readonly contractAddressesOutputPath: string;
    public readonly uploadBlockNumbersOutputPath: string;
    public readonly controllerAddress: string|undefined;
    public readonly createGenesisUniverse: boolean;
    public readonly useNormalTime: boolean;
    public readonly isProduction: boolean;
    public readonly legacyRepAddress: string;

    public constructor(contractInputRoot: string, artifactOutputRoot: string, controllerAddress: string|undefined, createGenesisUniverse: boolean=true, isProduction: boolean=false, useNormalTime: boolean=true, legacyRepAddress: string=PRODUCTION_LEGACY_REP_CONTRACT_ADDRESS) {
        this.isProduction = isProduction;
        this.controllerAddress = controllerAddress;
        this.createGenesisUniverse = createGenesisUniverse;
        this.useNormalTime = isProduction || useNormalTime;
        this.legacyRepAddress = legacyRepAddress;

        this.contractAddressesOutputPath = path.join(artifactOutputRoot, 'addresses.json');
        this.uploadBlockNumbersOutputPath = path.join(artifactOutputRoot, 'upload-block-numbers.json');
        this.contractInputPath = path.join(contractInputRoot, 'contracts.json');
    }

    public static create(artifactOutputRoot: string=ARTIFACT_OUTPUT_ROOT, isProduction: boolean=false, legacyRepAddress: string=PRODUCTION_LEGACY_REP_CONTRACT_ADDRESS): DeployerConfiguration {
        const contractInputRoot = (typeof process.env.CONTRACT_INPUT_ROOT === 'undefined') ? path.join(__dirname, '../../output/contracts') : path.normalize(<string> process.env.CONTRACT_INPUT_ROOT);
        const controllerAddress = process.env.AUGUR_CONTROLLER_ADDRESS;
        const createGenesisUniverse = (typeof process.env.CREATE_GENESIS_UNIVERSE === 'undefined') ? true : process.env.CREATE_GENESIS_UNIVERSE === 'true';
        const useNormalTime = (typeof process.env.USE_NORMAL_TIME === 'string') ? process.env.USE_NORMAL_TIME === 'true' : true;
        isProduction = (typeof process.env.IS_PRODUCTION === 'string') ? process.env.IS_PRODUCTION === 'true' : isProduction;

        return new DeployerConfiguration(contractInputRoot, artifactOutputRoot, controllerAddress, createGenesisUniverse, isProduction, useNormalTime, legacyRepAddress);
    }

    public static createWithControlledTime(legacyRepAddress: string=PRODUCTION_LEGACY_REP_CONTRACT_ADDRESS, isProduction: boolean=false, artifactOutputRoot: string=ARTIFACT_OUTPUT_ROOT): DeployerConfiguration {
        const contractInputRoot = (typeof process.env.CONTRACT_INPUT_ROOT === 'undefined') ? path.join(__dirname, '../../output/contracts') : path.normalize(<string> process.env.CONTRACT_INPUT_ROOT);
        const controllerAddress = process.env.AUGUR_CONTROLLER_ADDRESS;
        const createGenesisUniverse = (typeof process.env.CREATE_GENESIS_UNIVERSE === 'undefined') ? true : process.env.CREATE_GENESIS_UNIVERSE === 'true';
        const useNormalTime = false;
        isProduction = (typeof process.env.IS_PRODUCTION === 'string') ? process.env.IS_PRODUCTION === 'true' : isProduction;

        return new DeployerConfiguration(contractInputRoot, artifactOutputRoot, controllerAddress, createGenesisUniverse, isProduction, useNormalTime, legacyRepAddress);
    }
}
