import * as EthjsAbi from 'ethjs-abi';
import * as EthjsQuery from 'ethjs-query';
import { CompilerOutputContractAbi } from 'solc';

interface TransactionOptions {
    to?: string,
    from?: string,
    // TODO: add support for some kind of big number
    value?: number;
    gas?: number;
    gasPrice?: number;
    constant?: boolean;
}

export type Contract = { [methodName: string]: ContractMethod };
type ContractMethod = (...vargs: any[]) => Promise<any>;

export function parseAbiIntoMethods(ethjsQuery: EthjsQuery, abi: (CompilerOutputContractAbi)[], defaultTransaction: TransactionOptions = {}): Contract {
    const result: { [methodName: string]: ContractMethod } = {};
    const items = abi.filter(item => item.type === 'function').forEach(item => {
        result[item.name] = async function(this: TransactionOptions, ...vargs: any[]) {
            const callConvention = (Object.assign({ constant: item.constant }, defaultTransaction, this)).constant ? 'call' : 'sendTransaction';
            const from = this.from || defaultTransaction.from;
            if (!from && callConvention === 'sendTransaction') throw new Error("Must have a `from`.");
            const to = this.to || defaultTransaction.to;
            if (!to) throw new Error("Must have a `to`.");
            const data = EthjsAbi.encodeMethod(item, vargs);
            const value = this.value || defaultTransaction.value;
            const gasPrice = this.gasPrice || defaultTransaction.gasPrice;
            const gas = (callConvention === 'sendTransaction') ? this.gas || defaultTransaction.gas || await ethjsQuery.estimateGas(Object.assign({ to: to, from: from, data: data }, value && {value: value })) : undefined;
            if (!gas && callConvention === 'sendTransaction') throw new Error("Must have a `gas` when calling non-constant method.");
            const transaction = Object.assign(
                {
                    to: to,
                    data: data,
                },
                from && { from: from },
                gas && { gas: gas },
                value && { value: value },
                gasPrice && { gasPrice: gasPrice },
            );
            const result = await ethjsQuery[callConvention](transaction);
            if (callConvention === 'call') {
                if (result === '0x') {
                    throw new Error(`Transaction failed for unknown reasons.\nMethod Name: ${item.name}\n${JSON.stringify(transaction)}`);
                }
                // CONSIDER: currently this only supports returning the first output of a function, not all of them
                return EthjsAbi.decodeMethod(item, result)[0];
            } else {
                return result;
            }
        };
    });
    return result;
}
