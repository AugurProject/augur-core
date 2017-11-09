export function stringTo32ByteHex(stringToEncode: string): string {
    return `0x${Buffer.from(stringToEncode, 'utf8').toString('hex').padEnd(64, '0')}`;
}

export async function sleep(milliseconds: number): Promise<void> {
    return new Promise<void>(resolve => setTimeout(resolve, milliseconds));
}

export async function resolveAll(promises: Iterable<Promise<any>>) {
    let firstError: Error|null = null;
    for (let promise of promises) {
        try {
            await promise;
        } catch(e) {
            firstError = firstError || e;
        }
    }
    if (firstError !== null) throw firstError;
}

