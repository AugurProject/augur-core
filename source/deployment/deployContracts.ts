#!/usr/bin/env node

// import * as fs from 'fs';
// import * as path from 'path';
// import { SolidityContractCompiler } from "../libraries/CompileSolidity";
// // import { ContractDeployment } from "../libraries/ContractDeployment";

// try {
//     // Compile contracts to single file
//     const inputDirectoryPath = path.join(__dirname, "../../source/contracts");
//     const outputDirectoryPath = path.join(__dirname, "../contracts");
//     const outputFileName = "augurCore";

//     const solidityContractCompiler = new SolidityContractCompiler(inputDirectoryPath, outputDirectoryPath, outputFileName);
//     const result = solidityContractCompiler.compileContracts().then(function (result) { console.log(result); });

//     // Instantiate blockchain & upload contracts to blockchain
//     const ethjs = new ContractDeployment('http://localhost:8545');
//     const abi = JSON.parse('[{"constant":false,"inputs":[{"name":"_controller","type":"address"}],"name":"setController","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getTypeName","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_target","type":"address"}],"name":"suicideFunds","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]');
//     const bytecode = "60606040525b336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055505b5b6102a0806100566000396000f30060606040526000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806392eefe9b14610054578063db0a087c146100a5578063eb03db73146100d6575b600080fd5b341561005f57600080fd5b61008b600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610127565b604051808215151515815260200191505060405180910390f35b34156100b057600080fd5b6100b86101cf565b60405180826000191660001916815260200191505060405180910390f35b34156100e157600080fd5b61010d600480803573ffffffffffffffffffffffffffffffffffffffff169060200190919050506101f8565b604051808215151515815260200191505060405180910390f35b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614151561018457600080fd5b816000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550600190505b5b919050565b60007f4170706c6500000000000000000000000000000000000000000000000000000090505b90565b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614151561025557600080fd5b8173ffffffffffffffffffffffffffffffffffffffff16ff5b5b9190505600a165627a7a72305820b3e9080299d6aa853a0af095053d53ba5f35f3cc51f66102be8276833a5806780029";
//     const defaultTxObject = {
//         // from: tester.a0,
//         // data: ,
//         // gas: 300000,
//     }
//     console.log(ethjs.uploadContracts(abi, bytecode, defaultTxObject));

//     // Submit test transaction(s)
// } catch (error) {
//     console.log(error.message);
// }


import * as TestRpc from 'ethereumjs-testrpc';
import * as HttpProvider from 'ethjs-provider-http';
import * as Eth from 'ethjs-query';
import * as EthContract from 'ethjs-contract';


async function startTestRpc(port): Promise<boolean> {
    try {
        const server = TestRpc.server();
        server.listen(port);
        return true;
    } catch (error) {
        throw error;
    }
}

async function doWork() {
    try {
        const port = 8545;
        await startTestRpc(port);

        const eth = new Eth(new HttpProvider('http://localhost:' + port));
        const contract = new EthContract(eth);

        const accounts = await eth.accounts();
        const abi = JSON.parse('[{"constant":false,"inputs":[{"name":"_controller","type":"address"}],"name":"setController","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getTypeName","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_target","type":"address"}],"name":"suicideFunds","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]');
        const bytecode = "60606040525b336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055505b5b6102a0806100566000396000f30060606040526000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806392eefe9b14610054578063db0a087c146100a5578063eb03db73146100d6575b600080fd5b341561005f57600080fd5b61008b600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610127565b604051808215151515815260200191505060405180910390f35b34156100b057600080fd5b6100b86101cf565b60405180826000191660001916815260200191505060405180910390f35b34156100e157600080fd5b61010d600480803573ffffffffffffffffffffffffffffffffffffffff169060200190919050506101f8565b604051808215151515815260200191505060405180910390f35b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614151561018457600080fd5b816000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550600190505b5b919050565b60007f4170706c6500000000000000000000000000000000000000000000000000000090505b90565b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614151561025557600080fd5b8173ffffffffffffffffffffffffffffffffffffffff16ff5b5b9190505600a165627a7a72305820b3e9080299d6aa853a0af095053d53ba5f35f3cc51f66102be8276833a5806780029";
        const defaultTxObject = { from: accounts[0], data: bytecode, gas: 300000 };

        const Apple = contract(abi, bytecode, defaultTxObject);
        const apple = await Apple.new();
        apple.getTypeName();
    } catch (error) {
        throw error;
    }
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit();
});
