#!/usr/bin/env node

import { Configuration } from '../libraries/Configuration';
import { ArtifactDeployer } from '../libraries/ArtifactDeployer';

export async function runCannedMarkets(networks: Array<string>) {
    console.log(`Canning markets on ${networks.length} different networks`);
    const configurations: Array<Configuration> = networks.map((network) => Configuration.network(network));
    for(let configuration of configurations) {
        const deployer = new ArtifactDeployer(configuration);
        await deployer.runCannedMarkets();
    }
}

if (require.main === module) {
    const networks: Array<string> = process.argv.slice(2);
    runCannedMarkets(networks).then(() => {
        console.log('Canning markets on all networks succeeded');
        process.exitCode = 0;
    }).catch((error) => {
        console.log('Deployment interrupted with error: ', error);
        process.exitCode = 1;
    });
}
