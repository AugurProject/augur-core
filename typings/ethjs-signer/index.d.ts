declare module 'ethjs-signer' {
    import { Transaction } from 'ethjs-shared';

    export function sign(transaction: Transaction, privateKey: string, bufferResult?: false): string;
    export function sign(transaction: Transaction, privateKey: string, bufferResult: true): Buffer;
    export function recover(transaction: string | Buffer, v: number, r: Buffer, s: Buffer): Buffer;
}
