import * as path from 'path';
import { Configuration } from './Configuration';
import { spawn, SpawnOptions } from 'child_process';

export class ArtifactDeployer {
    private readonly configuration: Configuration;

    public constructor(configuration: Configuration) {
        this.configuration = configuration;
    }

    public async runCannedMarkets(): Promise<void> {
        if (this.configuration.networkName === null) {
            throw new Error('Must have a network name to can markets');
        } else if(!this.configuration.networkName.match(/[a-zA-Z0=9\-_]+/)) {
            throw new Error('Network names must consist of only alphanumeric chatacters and - or _');
        }

        console.log('\n\nStarted canning markets on:', this.configuration.networkName,'\n-----------------');

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

        await new Promise<void>((resolve, reject) => {
            const child = spawn(cannedMarketsScript, [<string> this.configuration.networkName], options);

            child.on('close', (code: number): void => {
                if (code !== 0) return reject(new Error('Market cannary exited with non-zero exit code'));
                resolve();
            });
        });

        console.log('\n\nFinished canning markets on:', this.configuration.networkName,'\n-----------------');
    }
}
