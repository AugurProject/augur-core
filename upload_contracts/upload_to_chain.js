#!/usr/bin/env node

"use strict";

var fs = require("fs");
var join = require("path").join;
var cp = require("child_process");
var async = require("async");
var abi = require("augur-abi");
var rpc = require("ethrpc");

var contractAddresses = {};
var noop = () => {};
var contractNames = ["mutex", "cash", "repContract"].concat(fs.readdirSync("../compiled").filter(name => name.slice(-7) === ".se.evm").map(name => name.slice(0, -7)));

rpc.setDebugOptions({ connect: true });
rpc.connect({
  httpAddresses: ["http://localhost:8545"],
  wsAddresses: ["ws://localhost:8546"],
  ipcAddresses: [],
  connectionTimeout: 3000,
  errorHandler: err => console.error(err)
}, () => {

  // 1. compile controller, make controller signature
  fs.readFile("../compiled/controller.se.evm", (err, contractFile) => {
    if (err) return console.error("readFile error:", err);

    // 2. upload controller
    rpc.transact({
      from: rpc.getCoinbase(),
      data: "0x" + contractFile.toString().trim(),
      send: true,
      returns: "null"
    }, null, noop, (r) => {
      rpc.getTransactionReceipt(r.hash, (receipt) => {
        if (!receipt || receipt.error) return console.error("getTransactionReceipt error:", receipt);
        console.log("contract address:", receipt.contractAddress);
        contractAddresses.controller = abi.format_address(receipt.contractAddress);

        // 3. bash ./deterministic_build.sh "0xactualControllerAddress"
        cp.exec("bash deterministic_build.sh " + contractAddresses.controller, (err, stdout, stderr) => {
          if (err) return console.error("deterministic build error:", err);
          console.log('stdout:', stdout.toString());

          // 4. upload deps ['mutex.se', 'cash.se', 'repContract.se'] are the ones so far, then the remaining contracts
          async.eachSeries(contractNames, (contractName, nextContract) => {
            if (contractAddresses[contractName]) return nextContract();
            console.log("uploading contractName:", contractName);
            fs.readFile("../compiled/" + contractName + ".se.evm", (err, contractFile) => {
              rpc.transact({
                from: rpc.getCoinbase(),
                data: "0x" + contractFile.toString().trim(),
                send: true,
                returns: "null"
              }, null, noop, (r) => {
                console.log("success:", contractName, r.hash);
                rpc.getTransactionReceipt(r.hash, (receipt) => {
                  if (!receipt || receipt.error) return nextContract(receipt || new Error("upload error"));
                  contractAddresses[contractName] = abi.format_address(receipt.contractAddress);

                  // 4a) do controller.setValue('contract', address) and self.controller.addToWhitelist(address) [can be in same block]
                  async.each([{
                    method: "setValue",
                    signature: ["int256", "int256"],
                    send: true,
                    returns: "int256",
                    from: rpc.getCoinbase(),
                    to: contractAddresses.controller,
                    params: [abi.short_string_to_int256(contractName), abi.format_int256(receipt.contractAddress)]
                  }, {
                    method: "addToWhitelist",
                    signature: ["int256"],
                    send: true,
                    returns: "int256",
                    from: rpc.getCoinbase(),
                    to: contractAddresses.controller,
                    params: [abi.format_int256(receipt.contractAddress)]
                  }], (tx, nextTx) => {
                    console.log(tx.method, tx);
                    rpc.transact(tx, null, noop, (r) => {
                      console.log(tx.method, "success:", r.callReturn, r.hash);
                      nextTx();
                    }, nextTx);
                  }, nextContract);
                });

                // 4b) go to the next contract in the list to upload
              }, nextContract);
            });
          }, (err) => {
            if (err) return console.error(err);
            fs.readFile("contracts.json", "utf8", (err, data) => {
              if (err) return console.error(err);
              var allContractAddresses = JSON.parse(data);
              allContractAddresses[rpc.getNetworkID()] = contractAddresses;
              fs.writeFile(join(process.env.AUGUR_CONTRACTS, "contracts.json"), JSON.stringify(allContractAddresses, null, 2), "utf8", (err) => {
                if (err) console.error(err);
                process.exit(0);
              });
            });
          });
        });
      });
    }, process.exit);
  });
});
