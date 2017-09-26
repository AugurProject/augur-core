#!/usr/bin/env node

// CONSIDER: Either expand this class to make it more useful, or eliminate it if we don't need any other functionality added to it.

import * as TestRpc from 'ethereumjs-testrpc';

export class RpcClient {
    public async listen(port): Promise<boolean> {
        const server = TestRpc.server();
        server.listen(port);
        return true;
    }
}
