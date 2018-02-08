declare module 'ethjs-account' {
    export interface Account {
        address: string;
        privateKey: string;
        publicKey: string;
    }
    export function generate(entropy: string): Account;
    export function getAddress(address: string): string;
    export function getChecksumAddress(address: string): string;
    export function sha3(publicKey: string): string;
    export function privateToPublic(privateKey: string): Buffer;
    export function publicToAddress(publicKey: Buffer): string;
    export function privateToAccount(privateKey: string): Account;
}
