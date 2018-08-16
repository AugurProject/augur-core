declare module '@velma/ganache-core' {
    interface TestRpcServer {
        listen(port: number, ): void;
        provider?: any;
    }
    export interface TestRpcAccount {
        balance: string;
        secretKey?: string;
    }
    export interface TestRpcServerOptions {
        accounts?: Array<TestRpcAccount>;
        debug?: boolean;
        logger?: { log?: (...args: Array<any>) => void };
        mnemoic?: string;
        port?: number;
        gasPrice?: string;
        gasLimit?: string;
        seed?: string;
        total_accounts?: number;
        fork?: string;
        network_id?: number;
        time?: number;
        locked?: boolean;
        unlocked_accounts?: Array<string>;
        db_path?: string;
    }
    export function server(options: TestRpcServerOptions): TestRpcServer;
}
