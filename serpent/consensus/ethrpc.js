/**
 * Send JSON-RPC commands to Ethereum from the safety and convenience of
 * your browser!
 * 
 * Examples:
 *   ETHRPC.eth("blockNumber");
 *   ETHRPC.db("putString", [ "testDB", "myKey", "myString" ]);
 *   ETHRPC.shh("version");
 * 
 * @author Jack Peterson (jack@augur.net)
 * @date 4/12/2015
 * @license MIT
 */
var ETHRPC = (function ($, rpc_url) {

    var addr, contracts, json, rpc;

    // post json-rpc command to ethereum client (tested w/ geth)
    function json_rpc(command, callback) {
        $.post(rpc_url, JSON.stringify(command), function (data) {
            if (data) {
                if (data.error) {
                    console.error(data.error);
                } else {
                    if (data.result && callback) {
                        callback(data);
                    } else {
                        console.log(data);
                    }
                }
            }
        });
    }

    function postdata(command, params, prefix) {
        data = { method: (prefix || "eth_") + command.toString() };
        if (params) {
            if (params.constructor === Array) {
                data.params = params;
            } else {
                data.params = [params];
            }
        }
        return data;
    }

    return {
        gasPrice: function () {
            json_rpc(postdata("gasPrice"), function (data) {
                var gas_price = parseInt(data.result);
                console.log("Gas price:", gas_price);
            });
        },
        getBalance: function (address) {
            json_rpc(postdata("getBalance", address), function (data) {
                var balance = parseInt(data.result) / 1e16;
                console.log("Balance:", balance);
            });
        },
        coinbase: function (addr) {
            json_rpc(postdata("coinbase"), function (data) {
                addr.coinbase = data.result;
                console.log("Coinbase:", addr.coinbase);
            });
        },
        sendTransaction: function (sender, compiled) {
            json_rpc(postdata("sendTransaction", {
                from: sender,
                gas: 10000000,
                data: compiled
            }), function (data) {
                addr.contract = data.result;
                console.log("Contract address:", addr.contract);
            });
        },
        eth: function (command, params, callback) {
            json_rpc(postdata(command, params), callback);
        },
        db: function (command, params, callback) {
            json_rpc(postdata(command, params, "db_"), callback);
        },
        shh: function (command, params, callback) {
            json_rpc(postdata(command, params, "shh_"), callback);
        }
    };
})(jQuery, "http://127.0.0.1:8545");

// frontier testnet addresses
addr = {
    jack: "0x63524e3fe4791aefce1e932bbfb3fdf375bfad89",
    branches: "0x8a26840f66bc222b0247ec922b821e14296c15ed"
};

// compiled contracts
contracts = {
    // mul2: multiply argument by 2 and return
    mul2: "0x604380600b600039604e567c010000000000000000000000000000000000000000000000000000000060003504636ffa1caa81141560415760043560405260026040510260605260206060f35b505b6000f3"
}

// test drive!
ETHRPC.gasPrice();
ETHRPC.getBalance(addr.jack);
ETHRPC.coinbase(addr);
ETHRPC.sendTransaction(addr.jack, contracts.mul2);
ETHRPC.eth("accounts");
ETHRPC.eth("blockNumber");
ETHRPC.db("putString", [ "testDB", "myKey", "myString" ]);
ETHRPC.db("getString", [ "testDB", "myKey" ]);
ETHRPC.shh("version");
