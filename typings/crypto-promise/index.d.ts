declare module 'crypto-promise' {
    type HashingAlgorithm = 'md5'|'sha1'|'sha3'|'sha256';
    type EncryptionAlgorithm = 'aes256';
    type DigestEncoding = 'hex'|'latin1'|'base64';
    type InputEncoding = 'utf8'|'ascii'|'latin1';
    interface Encoded {
        toString(encoding: DigestEncoding): string;
        toString(): Buffer;
    }
    interface Decoded { toString: () => string; }
    type Applicator = (data: string|Buffer, encoding?: InputEncoding) => Promise<Encoded>;
    type Deapplicator = (digest: string|Buffer, encoding?: DigestEncoding) => Promise<Decoded>;
    export function hash(algorithm: HashingAlgorithm): Applicator;
    export function hmac(algorithm: HashingAlgorithm, secret: string): Applicator;
    export function cipher(algorithm: EncryptionAlgorithm, secret: string): Applicator;
    export function decipher(algorithm: EncryptionAlgorithm, secret: string): Deapplicator;
    export function randomBytes(numberOfBytes: number): Promise<Buffer>;
}
