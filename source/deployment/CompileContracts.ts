import * as path from "path";
import { SolidityContractCompiler } from "../libraries/CompileSolidity";
require('source-map-support').install();

const CONTRACT_INPUT_DIR_PATH = path.join(__dirname, "../../source/contracts");
const CONTRACT_OUTPUT_DIR_PATH = path.join(__dirname, "../../output/contracts");
const COMPILED_CONTRACT_OUTPUT_FILE_NAME = "augurCore";

async function doWork(): Promise<void> {
    const compiler = new SolidityContractCompiler(CONTRACT_INPUT_DIR_PATH, CONTRACT_OUTPUT_DIR_PATH, COMPILED_CONTRACT_OUTPUT_FILE_NAME);
    await compiler.compileContracts();
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit();
});
