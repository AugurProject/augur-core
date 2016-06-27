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
                    contract_paths[f[0].upper() + f[1:-3]] = os.path.join(directory, f)
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
    send, returns = None, None
    if old_api and contract_name in old_api and method_name in old_api[contract_name]:
        if "send" in old_api[contract_name][method_name]:
            send = old_api[contract_name][method_name]["send"]
        if "returns" in old_api[contract_name][method_name]:
            returns = old_api[contract_name][method_name]["returns"]
    return send, returns

def update_from_old_api(method, contract_name, method_name, old_api):
    send, returns = get_send_returns(contract_name, method_name, old_api)
    if send is not None: method["send"] = send
    if returns is not None: method["returns"] = returns
    return method

def get_input_names(inputs):
    return [i["name"] for i in inputs]

def get_input_types(inputs):
    return [i["type"] for i in inputs]

def update_from_full_signature(name, inputs):
    split_name = name.split("(")
    method = {"method": split_name[0]}
    if len(inputs):
        method["signature"] = get_input_types(inputs)
        method["inputs"] = get_input_names(inputs)
    return method

# Generate each contract's full signature and update its API info
def update_contract_api(contract_name, contract_path, old_api):
    fullsig = serpent.mk_full_signature(contract_path)
    api = {}
    for fn in fullsig:
        if fn["type"] == "function":
            method = update_from_full_signature(fn["name"], fn["inputs"])
            api[method["method"]] = update_from_old_api(method, contract_name, method["method"], old_api)
    return api

# Update the API info for all Augur contracts
def update_api(contract_paths, old_api):
    bar = Bar("Contracts", max=len(contract_paths))
    new_api = {}
    for contract_name, contract_path in contract_paths.items():
        new_api[contract_name] = update_contract_api(contract_name, contract_path, old_api)
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
