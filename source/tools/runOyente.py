from oyente.oyente import run_solidity_analysis
from oyente.input_helper import InputHelper
from oyente.source_map import SourceMap
from oyente import global_params
from os import path, walk

import argparse
import logging
import sys

BASE_PATH = path.dirname(path.abspath(__file__))
def resolveRelativePath(relativeFilePath):
    return path.abspath(path.join(BASE_PATH, relativeFilePath))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--analyze", help="Do some sort of programatic analysis. Right now nothing interesting. Later!", action="store_true")
    parser.add_argument("-p", "--prettyprint", help="Pretty print results of the run like the oyente tool typically does", action="store_true")
    parser.add_argument("-v", "--verbose", help="Print verbose output", action="store_true")

    input_args = parser.parse_args()

    inputs = generate_inputs()

    if input_args.prettyprint or input_args.verbose:
        root = logging.getLogger()
        ch = logging.StreamHandler(sys.stdout)
        if input_args.verbose:
            root.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
        elif input_args.prettyprint:
            root.setLevel(logging.INFO)
            ch.setLevel(logging.INFO)
        root.addHandler(ch)

    global_params.CHECK_ASSERTIONS = 1

    results, exit_code = run_solidity_analysis(inputs)

    if input_args.analyze:
        analyze_results(results)

    exit(exit_code)

def generate_inputs():
    inputs = []
    for directory, _, filenames in walk(resolveRelativePath('../contracts')):
        if 'libraries' in directory: continue
        if 'legacy_reputation' in directory: continue
        for filename in filenames:
            name = path.splitext(filename)[0]
            extension = path.splitext(filename)[1]
            if extension != '.sol': continue
            if name.startswith('I'): continue
            if name.startswith('Base') : continue
            inputHelper = InputHelper(
                InputHelper.SOLIDITY,
                source=path.join(directory, filename),
                compilation_err=True,
                root_path="",
                remap='=%s/' % resolveRelativePath("../contracts"))
            inputs += inputHelper.get_inputs()
            SourceMap.parent_filename = ""
    return inputs

def analyze_results(results):
    for contractPath, contracts in results.items():
        for contract, data in contracts.items():
            for vuln, vuln_data in data['vulnerabilities'].items():
                if len(vuln_data) > 0:
                    print 'Vulnerability in contract %s: %s: %s' % (contract, vuln, vuln_data)

if __name__ == '__main__':
    main()
