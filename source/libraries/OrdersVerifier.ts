import { Connector } from '../libraries/Connector';
import { AccountManager } from '../libraries/AccountManager';
import { NetworkConfiguration } from '../libraries/NetworkConfiguration';
import { Orders, Market } from '../libraries/ContractInterfaces';
import * as Parallel from 'async-parallel';
import BN = require('bn.js');

const ORDERS = "0xd7a14019aeeba25e676a1b596bb19b6f37db74d2";

export interface Data {
    markets: Array<string>;
    orders: Array<string>;
}

export class OrdersVerifier {
    private data: Data;
    private ordersContract : Orders;
    private liveOrders: Array<string>;
    private foundOrders: Array<string>;
    private readonly sleepTimeInMS: number;

    private readonly connector: Connector;
    private readonly accountManager: AccountManager;

    private constructor(data: Data, ordersContract: Orders, connector: Connector, accountManager: AccountManager) {
        this.data = data;
        this.ordersContract = ordersContract;
        this.connector = connector;
        this.accountManager = accountManager;
        this.liveOrders = [];
        this.foundOrders = [];
        this.sleepTimeInMS = 5;
    }

    private async initialize(): Promise<void> {
        console.log("Getting live orders from input data");
        await this.getLiveOrders();
    }

    public static create = async (data: Data): Promise<OrdersVerifier> => {
        const networkConfiguration = NetworkConfiguration.create();
        const connector = new Connector(networkConfiguration);
        console.log(`Waiting for connection to: ${networkConfiguration.networkName} at ${networkConfiguration.http}`);
        await connector.waitUntilConnected();
        const accountManager = new AccountManager(connector, networkConfiguration.privateKey);

        const ordersContract = new Orders(connector, accountManager, ORDERS, connector.gasPrice);

        const ordersVerifier = new OrdersVerifier(data, ordersContract, connector, accountManager);
        await ordersVerifier.initialize();

        return ordersVerifier;
    }

    public async verify(): Promise<void> {

        await Parallel.each(this.data.markets, async marketId => {
            const market = new Market(this.connector, this.accountManager, marketId, this.connector.gasPrice);
            const numOutcomes = await market.getNumberOfOutcomes_();
            await Parallel.each(Array.from(Array(numOutcomes.toNumber()).keys()), async outcome => {
                await Parallel.each(Array.from(Array(2).keys()), async orderType => {
                    let marketOrderCount = 0;
                    let orderId = await this.ordersContract.getBestOrderId_(new BN(orderType), marketId, new BN(outcome));
                    if (orderId === "0x0000000000000000000000000000000000000000000000000000000000000000") return;
                    this.foundOrders.push(orderId);
                    marketOrderCount++;
                    let worseOrderId = await this.ordersContract.getWorseOrderId_(orderId);
                    while (worseOrderId !== "0x0000000000000000000000000000000000000000000000000000000000000000") {
                        this.foundOrders.push(worseOrderId);
                        marketOrderCount++;
                        orderId = worseOrderId;
                        worseOrderId = await this.ordersContract.getWorseOrderId_(orderId);
                    }
                }, 1);
            }, 1);
        }, 1);

        let missing = this.liveOrders.filter(item => this.foundOrders.indexOf(item) < 0);
        console.log("NUM MISSING ORDERS: ", missing.length);
        console.log("MISSING ORDERS: ", missing);

        return;
    }

    private async getLiveOrders(): Promise<void> {
        let i = 0;
        await Parallel.each(this.data.orders, async orderId => {
            await this.addToLiveOrdersIfLive(orderId);
            i++;
            if (i % 100 == 0) console.log(`${i} orders scanned`)
            await Parallel.sleep(this.sleepTimeInMS);
        }, 1);

        return;
    }

    private async addToLiveOrdersIfLive(orderId: string): Promise<void> {
        const balance = await this.ordersContract.getAmount_(orderId);
        if (!balance.isZero()) {
            this.liveOrders.push(orderId);
            if (this.liveOrders.length % 100 == 0) console.log(`${this.liveOrders.length} orders collected`)
        }
        return;
    }
}
