import BN = require('bn.js');
import { Account, generate, privateToAccount } from 'ethjs-account';
import { Transaction } from 'ethjs-shared';
import { sign } from 'ethjs-signer';
import { Connector } from './Connector';

export class AccountManager {
    private readonly connector: Connector;
    private readonly accounts = new Map<string, Account>();
    public readonly nonces = new Map<string, BN>();
    public readonly defaultAddress: string;

    constructor(connector: Connector, privateKey?: string) {
        this.connector = connector;
        const account = generate('non entropic entropy for account seed');
        this.accounts.set(account.address, account);
        this.defaultAddress = account.address;

        if (typeof privateKey !== 'undefined') {
            this.defaultAddress = this.addAccount(privateKey);
        }
    }

    public addAccount(privateKey: string): string {
        const account = privateToAccount(privateKey);
        this.accounts.set(account.address, account);
        return account.address;
    }

    public async getNonce(address: string): Promise<BN> {
        if (!this.accounts.has(address)) throw new Error(`Nonce requested for an account not managed by this Account Manager.  Requested address: ${address}`);

        if (this.nonces.has(address)) {
            const nonce = this.nonces.get(address)!.add(new BN(1));
            this.nonces.set(address, nonce);
            return nonce;
        } else {
            let nonce = await this.connector.ethjsQuery.getTransactionCount(address);
            // check to see if someone else already snagged a nonce before our await returned
            if (this.nonces.has(address)) {
                nonce = this.nonces.get(address)!.add(new BN(1));
            }
            this.nonces.set(address, nonce);
            return nonce;
        }
    }

    public async signTransaction(transaction: Transaction): Promise<string> {
        const sender = transaction.from || this.defaultAddress;
        if (typeof transaction.data === 'undefined') throw new Error(`transaction.data was undefined.`);
        if (typeof transaction.gas === 'undefined') throw new Error(`transaction.gas was undefined.`);
        if (typeof transaction.gasPrice === 'undefined') throw new Error(`transaction.gasPrice was undefined.`);
        const nonce = await this.getNonce(sender);
        const transactionToSend = Object.assign(
            {
                from: sender,
                data: transaction.data,
                gas: transaction.gas,
                gasPrice: transaction.gasPrice,
                nonce: nonce,
            },
            transaction.to ? { to: transaction.to } : <{to:string}>{},
            transaction.value ? { value: transaction.value } : <{value:BN}>{},
        );
        return sign(transactionToSend, this.accounts.get(sender)!.privateKey);
    }
}
