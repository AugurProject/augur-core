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
import re
import shutil
import subprocess
import getopt
import requests
import serpent
import sha3
from copy import deepcopy
from progress.bar import Bar

HERE = os.path.abspath(os.path.dirname(__file__))
SRC_EXTERN = os.path.abspath(os.path.join(HERE, os.pardir, "src"))

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
        if "functions" in old_api:
            old_api = old_api["functions"]
    return old_api

# Download contract API info from a remote host (Github)
def get_remote_api(api_url):
    print("Download api.json: " + api_url)
    response = requests.get(api_url)
    if response.status_code == 200:
        try:
            return response.json()["functions"]
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
    send, returns, mutable, gas, parser, fixed, label, description = None, None, None, None, None, None, None, None
    if old_api and contract_name in old_api and method_name in old_api[contract_name]:
        if "send" in old_api[contract_name][method_name]:
            send = old_api[contract_name][method_name]["send"]
        if "returns" in old_api[contract_name][method_name]:
            returns = old_api[contract_name][method_name]["returns"]
        if "mutable" in old_api[contract_name][method_name]:
            mutable = old_api[contract_name][method_name]["mutable"]
        if "gas" in old_api[contract_name][method_name]:
            gas = old_api[contract_name][method_name]["gas"]
        if "parser" in old_api[contract_name][method_name]:
            parser = old_api[contract_name][method_name]["parser"]
        if "fixed" in old_api[contract_name][method_name]:
            fixed = old_api[contract_name][method_name]["fixed"]
        if "label" in old_api[contract_name][method_name]:
            label = old_api[contract_name][method_name]["label"]
        if "description" in old_api[contract_name][method_name]:
            description = old_api[contract_name][method_name]["description"]
    return send, returns, mutable, gas, parser, fixed, label, description

def update_from_old_api(method, contract_name, method_name, old_api):
    send, returns, mutable, gas, parser, fixed, label, description = get_send_returns(contract_name, method_name, old_api)
    if send is not None: method["send"] = send
    if returns is not None: method["returns"] = returns
    if mutable is not None: method["mutable"] = mutable
    if gas is not None: method["gas"] = gas
    if parser is not None: method["parser"] = parser
    if fixed is not None: method["fixed"] = fixed
    if label is not None: method["label"] = label
    if description is not None: method["description"] = description
    return method

def get_input_names(inputs):
    return [i["name"] for i in inputs]

def get_input_types(inputs):
    return [i["type"] for i in inputs]

def get_fixedpoint_inputs(input_list):
    fxp_inputs = []
    for i, input_name in enumerate(input_list):
        if input_name.startswith("fxp"):
            fxp_inputs.append(i)
    return fxp_inputs

def make_method_label(method):
    label = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', method)
    return label[0].upper() + label.replace('_', ' ')[1:]

def update_from_full_signature(name, inputs, outputs):
    split_name = name.split("(")
    method = {"method": split_name[0]}
    method["label"] = make_method_label(method["method"])
    if len(inputs):
        method["signature"] = get_input_types(inputs)
        method["inputs"] = get_input_names(inputs)
        fxp_inputs = get_fixedpoint_inputs(method["inputs"])
        if len(fxp_inputs): method["fixed"] = fxp_inputs
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
                "signature": "0x" + sha3.sha3_256(evt["name"].encode("ascii")).hexdigest(),
                "contract": contract_name
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

def get_fixedpoint_outputs(contract_path):
    has_fixedpoint_output = []
    with open(contract_path) as srcfile:
        for linenum, line in enumerate(srcfile):
            if line.startswith("def "):
                if prevline == "# @return fxp\n":
                    has_fixedpoint_output.append(line.split("def ")[1].split("(")[0])
            prevline = line
    return has_fixedpoint_output

# Generate a contract's full signature and update its API info
def update_contract_api(contract_name, contract_path, old_api):
    fullsig = serpent.mk_full_signature(contract_path)
    if type(fullsig) == str or type(fullsig) == buffer:
        fullsig = json.loads(fullsig)
    events_api = update_contract_events_api(contract_name, fullsig)
    functions_api = update_contract_functions_api(contract_name, fullsig, old_api)
    fixedpoint_output_methods = get_fixedpoint_outputs(contract_path)
    for method_name in fixedpoint_output_methods:
        if method_name != "init" and method_name != "any" and method_name != "shared":
            functions_api[method_name]["returns"] = "unfix"
    return events_api, functions_api

def extract_macros(contract_path):
    macros = []
    with open(contract_path) as srcfile:
        startline = None
        for linenum, line in enumerate(srcfile):
            if line.startswith("inset("):
                inset_filename = line.strip().split("inset(")[1].split(")")[0].strip("'").strip("\"")
                inset_filename = os.path.join(os.path.dirname(os.path.abspath(contract_path)), inset_filename)
                macros.extend(extract_macros(inset_filename))
            if line.startswith("macro ") and "(" in line:
                macros.append(line.strip().split("macro ")[1].split(":")[0].split("(")[0])
    return list(set(macros))

def get_events_in_method(contract_path, method_name, all_methods):
    events_in_method = []
    check_methods = deepcopy(all_methods)
    for i, submethod in enumerate(check_methods):
        if submethod["method"] == method_name:
            check_methods.pop(i)
    with open(contract_path) as srcfile:
        startline = None
        submethods = []
        for linenum, line in enumerate(srcfile):
            if startline is not None:
                if line.strip().startswith("log(type="):
                    events_in_method.append(line.strip().split("log(type=")[1].split(",")[0])
                if line.startswith("def ") or line.startswith("macro "):
                    break
                for i, submethod in enumerate(check_methods):
                    if submethod["finder"] in line:
                        check_method = check_methods.pop(i)
                        already_appended = False
                        for s in submethods:
                            if s["method"] == check_method["method"]:
                                already_appended = True
                        if not already_appended:
                            submethods.append(check_method)
            if line.startswith("def " + method_name) or line.startswith("macro " + method_name):
                startline = linenum
    for submethod in submethods:
        submethod_events = get_events_in_method(submethod["contract_path"], submethod["method"], check_methods)
        if len(submethod_events):
            print("  - " + submethod["method"])
            events_in_method.extend(submethod_events)
    events_in_method = list(set(events_in_method))
    return events_in_method

# Update the API info for all Augur contracts
def update_api(contract_paths, old_api):
    bar = Bar("Contracts", max=len(contract_paths))
    new_api = {"events": {}, "functions": {}}
    all_methods = []
    for contract_name, contract_path in contract_paths.items():
        events_api, functions_api = update_contract_api(contract_name, contract_path, old_api)
        if bool(events_api): new_api["events"].update(events_api)
        contract_methods_list = []
        for contract_method in functions_api.keys():
            if contract_name != "CompositeGetters" and not contract_method.startswith("get"):
                contract_methods_list.append({
                    "method": contract_method,
                    "contract_path": contract_path,
                    "finder":  "." + contract_method + "("
                })
        if "data_api" not in contract_path:
            for macro in extract_macros(contract_path):
                contract_methods_list.append({
                    "method": macro,
                    "contract_path": contract_path,
                    "finder": macro + "("
                })
        all_methods.extend(contract_methods_list)
        new_api["functions"][contract_name] = functions_api
        bar.next()
    bar.finish()
    for contract_name, contract_path in contract_paths.items():
        functions_api = new_api["functions"][contract_name]
        for method_name in functions_api.keys():
            if contract_name != "CompositeGetters" and not method_name.startswith("get"):
                print(contract_name + "." + method_name)
                events_in_method = get_events_in_method(contract_path, method_name, all_methods)
                if len(events_in_method):
                    print("    events: " + str(events_in_method))
                    new_api["functions"][contract_name][method_name]["events"] = events_in_method
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
    old_api = get_old_api(input_path, isLocal=isLocal)
    new_api = update_api(get_contract_paths(SRC_EXTERN), old_api)
    write_new_api(new_api, output_path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
