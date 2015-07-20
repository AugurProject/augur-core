#!/usr/bin/env node
/**
 * Augur contract method caller.
 *
 * Syntax: node call_contract.js <call/send> <method name> <arguments>
 *
 * Examples:
 * node call_contract.js call getRepBalance 1010101 0x63524e3fe4791aefce1e932bbfb3fdf375bfad89
 * node call_contract.js send sendCash 0x6fc0a64e2dce367e35417bfd1568fa35af9f3e4b 10
 *
 * @author Jack Peterson (jack@tinybike.net)
 */

var Augur = require("augur.js");
var log = console.log;

Augur.options.BigNumberOnly = false;
Augur.connect();

var tx = Augur.tx[process.argv[3]];

tx.send = process.argv[2] === "send";
tx.params = process.argv.slice(4);

function echo(label, output) {
    log(label);
    if (output && output.constructor === Object || output.constructor === Array) {
        log(JSON.stringify(output, null, 2));
    } else {
        log(output);
    }
}

echo("TX:", tx);

if (tx.send) {
    Augur.send_call_confirm(tx,
        function (output) { echo("SENT:", output); },
        function (output) { echo("SUCCESS:", output); },
        function (output) { echo("FAILED:", output); }
    );
} else {
    Augur.fire(tx, function (output) { echo("OUTPUT:", output); });
}
