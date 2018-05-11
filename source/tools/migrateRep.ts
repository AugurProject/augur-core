#!/usr/bin/env node

require('source-map-support').install();
import * as fs from "async-file";
import { LegacyRepMigrator } from '../libraries/LegacyRepMigrator';
import * as yargs from 'yargs';

let argv =  yargs
    .option('repAddress', {
        describe: "Address of the new REP contract to migrates to",
    })
    .option('balances', {
        describe: "File containing newline delimited addresses that have REP balances",
    })
    .option('allowanceOwners', {
        describe: "File containing newline delimited addresses for the allowance owners",
    })
    .option('allowanceSpenders', {
        describe: "File containing newline delimited addresses that the allowance spenders",
    })
    .option('chunkSize', {
        describe: "Number of addresses to use per TX",
        default: 25,
    })
.help()
.demandOption(['repAddress', 'balances', 'allowanceOwners', 'allowanceSpenders'], 'Please provide required arguments')
.argv;

async function doWork(): Promise<void> {
    const balancesFileContents = await fs.readFile(argv.balances);
    const allowanceOwnersFileContents = await fs.readFile(argv.allowanceOwners);
    const allowanceSpendersFileContents = await fs.readFile(argv.allowanceSpenders);

    const balances = balancesFileContents.split('\n');
    const allowanceOwners = allowanceOwnersFileContents.split('\n');
    const allowanceSpenders = allowanceSpendersFileContents.split('\n');

    const legacyRepData = {
        balances,
        allowanceOwners,
        allowanceSpenders,
    }

    const repContractAddress = argv.repAddress;
    const chunkSize = argv.chunkSize;

    const legacyRepMigrator: LegacyRepMigrator = await LegacyRepMigrator.create(legacyRepData, repContractAddress, chunkSize);
    await legacyRepMigrator.migrateLegacyRep();
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit(1);
});