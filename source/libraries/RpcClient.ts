#!/usr/bin/env node

// CONSIDER: Either expand this class to make it more useful, or eliminate it if we don't need any other functionality added to it.

import * as TestRpc from 'ethereumjs-testrpc';

export class RpcClient {
    public async listen(port): Promise<boolean> {
        // Set gas block limit extremely high so new blocks don't have to be mined while uploading contracts
        const gasBlockLimit = Math.pow(2, 32);
        const server = TestRpc.server({gasLimit: gasBlockLimit});
        server.listen(port);
        return true;
    }
}
