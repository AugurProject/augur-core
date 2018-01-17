import * as path from 'path';
import { promisify } from 'util';
import { Configuration } from './Configuration';
import { spawn, SpawnOptions } from 'child_process';
const spawnAsync = promisify(spawn);

export class ArtifactDeployer {
    private readonly configuration: Configuration;

    public constructor(configuration: Configuration) {
        this.configuration = configuration;
    }

    public async runCannedMarkets(): Promise<void> {
        if (this.configuration.networkName === null) {
            throw new Error('Must have a network name to can markets');
        }

        const options: SpawnOptions = {
            env: {
                ETHEREUM_PRIVATE_KEY: this.configuration.privateKey,
                PATH: process.env.PATH
            },
            cwd: this.configuration.augurjsRepoPath,
            shell: true,
            stdio: 'inherit'
        };

        const cannedMarketsScript = path.join(this.configuration.augurjsRepoPath, 'scripts', 'canned-markets.sh');
        await spawnAsync(cannedMarketsScript, [this.configuration.networkName], options);
    }
}
