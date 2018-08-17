declare module '@velma/ganache-core' {
    export interface GanacheCoreProvider {
    }
     export interface GanacheCoreServer {
        provider: GanacheCoreProvider;
        listen(): void;
    }
     export function server(options: any): GanacheCoreServer;
     export function provider(options: any): GanacheCoreProvider;
}
