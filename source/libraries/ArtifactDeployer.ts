import * as path from 'path';
import { promisify } from 'util';
import { Configuration } from './Configuration';
import { execFile, ExecFileOptions } from 'child_process';
const execFileAsync = promisify(execFile);

export class ArtifactDeployer {
    private readonly configuration: Configuration;

    public constructor(configuration: Configuration) {
        this.configuration = configuration;
    }

    public async runCannedMarkets(): Promise<void> {
        if (this.configuration.networkName === null) {
            throw new Error('Must have a network name to can markets');
        }

        const options: ExecFileOptions = {
            env: {
                ETHEREUM_PRIVATE_KEY: this.configuration.privateKey
            },
            cwd: this.configuration.augurjsRepoPath,
        };

        const cannedMarketsScript = path.join(this.configuration.augurjsRepoPath, 'scripts', 'canned-markets.sh');
        const { stdout } = await execFileAsync(cannedMarketsScript, [this.configuration.networkName], options);

        console.log(stdout);
    }
}
