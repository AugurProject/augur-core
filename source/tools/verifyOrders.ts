#!/usr/bin/env node

require('source-map-support').install();
import * as fs from "async-file";
import { OrdersVerifier } from '../libraries/OrdersVerifier';
import * as yargs from 'yargs';

let argv =  yargs
    .option('markets', {
        describe: "File containing newline delimited addresses of created markets",
    })
    .option('orders', {
        describe: "File containing newline delimited ids of created orders",
    })
.help()
.demandOption(['markets', 'orders'], 'Please provide required arguments')
.argv;

async function doWork(): Promise<void> {
    const marketsFileContents = await fs.readFile(argv.markets, 'utf8');
    const ordersFileContents = await fs.readFile(argv.orders, 'utf8');

    const markets = marketsFileContents.split('\n');
    const orders = ordersFileContents.split('\n');

    const data = {
        markets,
        orders,
    }

    const ordersVerifier: OrdersVerifier = await OrdersVerifier.create(data);
    await ordersVerifier.verify();
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit(1);
});
