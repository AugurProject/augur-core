#!/usr/bin/env python
# Copyright (c) 2017 Christian Calderon

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import print_function
import argparse
import serpent
import os
import re
import binascii
import json
import shutil
import sys
import multiprocessing
import requests
import tempfile

if (3, 0) <= sys.version_info:
    _old_mk_signature = serpent.mk_signature
    def mk_signature(code):
        return _old_mk_signature(code).decode()
    serpent.mk_signature = mk_signature

WORKER_POOL_SIZE = 2

PYNAME = '[A-Za-z_][A-Za-z0-9_]*'
IMPORT = re.compile('import ({0}) as ({0})'.format(PYNAME))
EXTERN = re.compile('extern ({}): .+'.format(PYNAME))

EXTERN_ERROR_MSG = 'Weird extern in {path} at line {line}: {eg}'
IMPORT_ERROR_MSG = 'Weird import in {path} at line {line}: {eg}'

# these are standard contracts that don't have a specific / unique controller address
STANDARD_EXTERNS = {
    'Controller': '',

    # ERC20 and aliases used in Augur code
    'ERC20': 'extern ERC20: [allowance:[address,address]:uint256, approve:[address,uint256]:uint256, balanceOf:[address]:uint256, decimals:[]:uint256, name:[]:uint256, symbol:[]:uint256, totalSupply:[]:uint256, transfer:[address,uint256]:uint256, transferFrom:[address,address,uint256]:uint256]',
    'subcurrency': 'extern subcurrency: [allowance:[address,address]:uint256, approve:[address,uint256]:uint256, balanceOf:[address]:uint256, decimals:[]:uint256, name:[]:uint256, symbol:[]:uint256, totalSupply:[]:uint256, transfer:[address,uint256]:uint256, transferFrom:[address,address,uint256]:uint256]',
    'wallet': 'extern wallet: [initialize:[int256]:int256, setWinningOutcomeContractAddressInitialize:[int256,int256]:int256, transfer:[address,uint256]:int256]',
    'rateContract': 'extern rateContract: [rateFunction:[]:int256]',
    'forkResolveContract': 'extern forkResolveContract: [resolveFork:[]:int256]',
    'shareTokens': 'extern shareTokens: [allowance:[address,address]:int256, approve:[address,uint256]:int256, balanceOf:[address]:int256, changeTokens:[int256,int256]:int256, getDecimals:[]:int256, getName:[]:int256, getSymbol:[]:int256, modifySupply:[int256]:int256, totalSupply:[]:int256, transfer:[address,uint256]:int256, transferFrom:[address,address,uint256]:int256]',
}

DEFAULT_RPCADDR = 'http://localhost:8545'
DEFAULT_CONTROLLER = ''

SERPENT_EXT = '.se'
MACRO_EXT = '.sem'

parser = argparse.ArgumentParser(description='Compiles collections of serpent contracts.',
                                 epilog='Try a command followed by -h to see it\'s help info.')
#parser.set_defaults(command='help')

commands = parser.add_subparsers(title='commands')

translate = commands.add_parser('translate', help='Translate imports to externs.')
translate.add_argument('-s', '--source', help='Directory to search for Serpent code', required=True)
translate.add_argument('-t', '--target', help='Directory to save translated code in.', required=True)
translate.set_defaults(command='translate')

update = commands.add_parser('update', help='Updates the externs in --source.')
update.add_argument('-s', '--source', help='Directory to search for Serpent code', required=True)
update.add_argument('-c', '--controller', help='The address in hex of the Controller contract.', default=None)
update.set_defaults(command='update')

compile_ = commands.add_parser('compile', help='Compiles and uploads all the contracts in --source. (TODO)')
compile_.add_argument('-s', '--source', help='Directory to search for Serpent code', required=True)
compile_.add_argument('-r', '--rpcaddr', help='Address of RPC server', default=DEFAULT_RPCADDR)
compile_.set_defaults(command='compile')


class ContractError(Exception):
    """Error class for all errors by load_contracts."""


def find_files(source_dir, extension):
    """Makes a list of paths in the directory which end in the extenstion."""
    paths = []
    for entry in os.listdir(source_dir):
        entry = os.path.join(source_dir, entry)
        if os.path.isfile(entry) and entry.endswith(extension):
            paths.append(entry)
        elif os.path.isdir(entry):
            paths.extend(find_files(entry, extension))
        else:
            continue
    return paths


def split_crud(code_lines):
    """Separates comment-crud at the top of the file from everything else."""
    crud = []
    noncrud = []

    for i, line in enumerate(code_lines):
        if line.startswith('#'):
            crud.append(line)
        else:
            noncrud.extend(code_lines[i:])
            break

    return crud, noncrud


def strip_dependencies(serpent_file):
    """Separates dependency information from Serpent code in the file."""

    with open(serpent_file) as f:
        code = f.read().split('\n')

    crud, code = split_crud(code)
    dependencies = []
    other_code = []

    for i, line in enumerate(code):
        if line.startswith('import'):
            m = IMPORT.match(line)
            if m:
                dependencies.append((m.group(1), m.group(2)))
            else:
                msg = IMPORT_ERROR_MSG.format(
                    path=serpent_file,
                    line=(i + len(crud)),
                    eq=line)
                raise ContractError(msg)
        else:
            other_code.append(line)

    if other_code[-1]:
        other_code.append('') # makes sure the file ends with a blank line

    crud.append('') # makes sure there is a blank line between crud and dependencies

    return dependencies, '\n'.join(other_code), '\n'.join(crud)


def imports_to_externs(source_dir, target_dir):
    """Translates code using import syntax to standard Serpent externs."""
    source_dir = os.path.abspath(source_dir)
    target_dir = os.path.abspath(target_dir)

    if os.path.exists(target_dir):
        raise ContractError('The target directory already exists!')

    tempdir = tempfile.mkdtemp()
    temp_target_copy = os.path.join(tempdir, os.path.basename(target_dir))
    shutil.copytree(source_dir, temp_target_copy)

    try:
        serpent_files = find_files(temp_target_copy, SERPENT_EXT)

        source_map = {}

        for path in serpent_files:
            name = os.path.basename(path).replace(SERPENT_EXT, '')
            info = {}
            info['dependencies'], info['stripped_code'], info['crud'] = strip_dependencies(path)
            
            with open(path, 'w') as temp:
                temp.write(info['stripped_code'])

            extern_name = 'extern {}:'.format(name)
            signature = serpent.mk_signature(path)
            name_end = signature.find(':') + 1
            signature = extern_name + signature[name_end:]
            info['signature'] = signature
            info['path'] = path
            source_map[name] = info

        lookup_fmt = '{} = Controller.lookup(\'{}\')'
        for name in source_map:
            info = source_map[name]
            signatures = [DEFAULT_CONTROLLER, # a place holder that needs to be updated before compiling
                          STANDARD_EXTERNS['Controller']]
            for oname, alias in info['dependencies']:
                signatures.append('')
                signatures.append(lookup_fmt.format(alias, oname))
                signatures.append(source_map[oname]['signature'])
            signatures.append('') # blank line between signatures section and rest of code
            new_code = '\n'.join([info['crud']] + signatures + [info['stripped_code']])
            path = info['path']

            with open(path, 'w') as f:
                f.write(new_code)
    except Exception:
        raise
    else:
        shutil.copytree(temp_target_copy, target_dir)
    finally:
        shutil.rmtree(tempdir)


def update_externs(source_dir, controller):
    """Updates all externs in source_dir."""
    if controller:
        new_controller = 'macro Controller: {}'.format(controller)
    source_dir = os.path.abspath(source_dir)
    tempdir = tempfile.mkdtemp()
    source_copy = os.path.join(tempdir, os.path.basename(source_dir))
    shutil.copytree(source_dir, source_copy)
    extern_map = STANDARD_EXTERNS.copy()


    try:
        serpent_files = find_files(source_copy, SERPENT_EXT)

        for path in serpent_files:
            name = os.path.basename(path).replace(SERPENT_EXT, '')
            extern_name = 'extern {}:'.format(name)
            signature = serpent.mk_signature(path)
            name_end = signature.find(':') + 1
            signature = extern_name + signature[name_end:]
            extern_map[name] = signature

        for path in serpent_files:
            with open(path) as f:
                code = f.read().split('\n')

            crud, code = split_crud(code)
            saw_controller = False

            for i in range(len(code)):

                m = EXTERN.match(code[i])

                if code[i].startswith('extern') and m is None:
                    msg = EXTERN_ERROR_MSG.format(path=path, line=(i + len(crud)), eg=code[i])
                    raise ContractError(msg)
                if m and m.group(1) not in extern_map:
                    msg = EXTERN_ERROR_MSG.format(path=path, line=(i + len(crud)), eg=code[i])
                    raise ContractError(msg)

                if m:
                    code[i] = extern_map[m.group(1)]
                elif code[i].startswith('macro Controller:'):
                    saw_controller = True
                    if controller:
                        code[i] = new_controller

            if not saw_controller:
                crud.append(DEFAULT_CONTROLLER)

            code = '\n'.join(crud + code)
            with open(path, 'w') as f:
                f.write(code)
    except Exception:
        raise
    else:
        shutil.rmtree(source_dir)
        shutil.copytree(source_copy, source_dir)
    finally:
        shutil.rmtree(tempdir)


def main():
    args = parser.parse_args()

    try:
        if args.command == 'help':
            parser.print_help()
        elif args.command == 'translate':
            imports_to_externs(args.source, args.target)
        elif args.command ==  'update':
            update_externs(args.source, args.controller)
        else:
            print('command not implemented:', args.command)
            return 1
    except ContractError as exc:
        print(exc.args[0])
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())