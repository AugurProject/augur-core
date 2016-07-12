#!/usr/bin/env python
"""Augur API maker.

The "API maker" generates static API info for Augur's smart contracts:
https://github.com/AugurProject/augur-contracts/blob/master/api.json

Usage:

    python make_api.py [flags]

Optional flags:

    -i, --inpath [/path/to/input/api.json]:
        Local filesystem path to augur-contracts/api.json.

    -o, --outpath [/path/to/output/api.json]:
        Local path where the updated api.json will be written.  If no output
        path is specified, the updated API is sent to stdout.
        (Warning: if this file exists, it will be overwritten.)

@author Jack Peterson (jack@tinybike.net)

"""
import sys
import os
import json
import shutil
import subprocess
import getopt
import requests
import serpent
import sha3
from progress.bar import Bar

HERE = os.path.abspath(os.path.dirname(__file__))
SRC_EXTERN = os.path.abspath(os.path.join(HERE, os.pardir, "src-extern"))

# If the translated (src-extern) directory exists, remove it
def remove_translated_contracts(path):
    if os.path.exists(path): shutil.rmtree(path)

# Translate the Augur contracts to standard Serpent extern syntax
def translate_contracts(path):
    subprocess.check_output([os.path.join(HERE, "load_contracts.py"), "-t", path])
    print("Translated contracts: " + path)

# Gather a list of contracts and source file paths within src-extern
def get_contract_paths(path):
    contract_paths = {}
    for directory, subdirs, files in os.walk(path):
        for f in files:
            if directory.endswith("data_api") or directory.endswith("functions"):
                if f.endswith(".se") and f not in ["output.se", "refund.se"] and not f.startswith(".~"):
                    contract_name = f[0].upper() + f[1:-3]
                    if contract_name == "Buy&sellShares": contract_name = "BuyAndSellShares"
                    contract_paths[contract_name] = os.path.join(directory, f)
    return contract_paths

# Get contract API info from a local file
def get_local_api(api_path):
    print("Load api.json from file: " + api_path)
    with open(api_path, "r") as api_file:
        old_api = json.load(api_file)
    return old_api

# Download contract API info from a remote host (Github)
def get_remote_api(api_url):
    print("Download api.json: " + api_url)
    response = requests.get(api_url)
    if response.status_code == 200:
        try:
            return response.json()
        except Exception as exc:
            print(exc)

# Read the existing contract API info from augur-contracts/api.json
def get_old_api(api_path, isLocal=False):
    old_api = None
    if api_path:
        old_api = get_local_api(api_path) if isLocal else get_remote_api(api_path)
    return old_api

# Retrieve "send" and/or "returns" values from the old API
def get_send_returns(contract_name, method_name, old_api):
    send, returns, mutable = None, None, None
    if old_api and contract_name in old_api and method_name in old_api[contract_name]:
        if "send" in old_api[contract_name][method_name]:
            send = old_api[contract_name][method_name]["send"]
        if "returns" in old_api[contract_name][method_name]:
            returns = old_api[contract_name][method_name]["returns"]
        if "mutable" in old_api[contract_name][method_name]:
            mutable = old_api[contract_name][method_name]["mutable"]
    return send, returns, mutable

def update_from_old_api(method, contract_name, method_name, old_api):
    send, returns, mutable = get_send_returns(contract_name, method_name, old_api)
    if send is not None: method["send"] = send
    if returns is not None: method["returns"] = returns
    if mutable is not None: method["mutable"] = mutable
    return method

def get_input_names(inputs):
    return [i["name"] for i in inputs]

def get_input_types(inputs):
    return [i["type"] for i in inputs]

def update_from_full_signature(name, inputs, outputs):
    split_name = name.split("(")
    method = {"method": split_name[0]}
    if len(inputs):
        method["signature"] = get_input_types(inputs)
        method["inputs"] = get_input_names(inputs)
    if outputs is not None and len(outputs) and "type" in outputs[0]:
        if outputs[0]["type"] == "bytes":
            method["returns"] = "string"
        else:
            method["returns"] = outputs[0]["type"]
    return method

def update_contract_events_api(contract_name, fullsig):
    api = {}
    for evt in fullsig:
        if evt["type"] == "event":
            split_name = evt["name"].split("(")
            api[split_name[0]] = {
                "inputs": evt["inputs"],
                "name": evt["name"],
                "signature": "0x" + sha3.sha3_256(evt["name"].encode("ascii")).hexdigest()
            }
    return api

def update_contract_functions_api(contract_name, fullsig, old_api):
    api = {}
    for fn in fullsig:
        if fn["type"] == "function" and fn["name"] != "test_callstack()":
            outputs = fn["outputs"] if "outputs" in fn else None
            method = update_from_full_signature(fn["name"], fn["inputs"], outputs)
            api[method["method"]] = update_from_old_api(method, contract_name, method["method"], old_api)
    return api

# Generate a contract's full signature and update its API info
def update_contract_api(contract_name, contract_path, old_api):
    fullsig = serpent.mk_full_signature(contract_path)
    events_api = update_contract_events_api(contract_name, fullsig)
    functions_api = update_contract_functions_api(contract_name, fullsig, old_api)
    return events_api, functions_api

# Update the API info for all Augur contracts
def update_api(contract_paths, old_api):
    bar = Bar("Contracts", max=len(contract_paths))
    new_api = {"events": {}, "functions": {}}
    for contract_name, contract_path in contract_paths.items():
        events_api, functions_api = update_contract_api(contract_name, contract_path, old_api)
        if bool(events_api): new_api["events"][contract_name] = events_api
        new_api["functions"][contract_name] = functions_api
        bar.next()
    bar.finish()
    return new_api

# Save the updated API info to a file (if path is set) or print to screen
def write_new_api(new_api, api_path):
    if api_path:
        with open(api_path, "w") as api_file:
            json.dump(new_api, api_file, indent=2, sort_keys=True)
            print("Wrote contract API file: " + api_path)
    else:
        print(json.dumps(new_api, indent=2, sort_keys=True))

def main(argv=None):
    if argv is None: argv = sys.argv
    try:
        short_opts = "hi:o:"
        long_opts = ["help", "inpath=", "outpath="]
        opts, vals = getopt.getopt(argv[1:], short_opts, long_opts)
    except getopt.GetoptError as e:
        sys.stderr.write(e.msg)
        sys.stderr.write("for help use --help")
        return 2
    input_path, output_path = None, None
    isLocal = False
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(__doc__)
            return 0
        elif opt in ("-i", "--inpath"):
            input_path = arg
        elif opt in ("-o", "--outpath"):
            output_path = arg
    if input_path is None:
        input_path = "https://raw.githubusercontent.com/AugurProject/augur-contracts/master/api.json"
    else:
        isLocal = True
    remove_translated_contracts(SRC_EXTERN)
    translate_contracts(SRC_EXTERN)
    old_api = get_old_api(input_path, isLocal=isLocal)
    new_api = update_api(get_contract_paths(SRC_EXTERN), old_api)
    write_new_api(new_api, output_path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
