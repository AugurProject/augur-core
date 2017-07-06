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
import os
import os.path
import errno
import re
from binascii import hexlify
import shutil
import sys
from serpent import mk_signature
import tempfile
import warnings
import ethereum.tester
import socket
import select

if (3, 0) <= sys.version_info:

    def pretty_signature(path, name):
        ugly_signature = mk_signature(path).decode()
        extern_name = 'extern {}:'.format(name)
        name_end = ugly_signature.find(':') + 1
        signature = extern_name + ugly_signature[name_end:]
        return signature

    _hexlify = hexlify

    def hexlify(binary):
        return _hexlify(binary).decode()
else:

    def pretty_signature(path, name):
        ugly_signature = mk_signature(path)
        extern_name = 'extern {}:'.format(name)
        name_end = ugly_signature.find(':') + 1
        signature = extern_name + ugly_signature[name_end:]
        return signature

IPC_SOCK = None

HOMESTEAD_BLOCK_NUMBER = 1150000

IMPORT = re.compile('^import (?P<name>\w+) as (?P<alias>\w+)$')
EXTERN = re.compile('^extern (?P<name>\w+): \[.+\]$')
CONTROLLER_V1 = re.compile('^(?P<indent>\s*)(?P<alias>\w+) = Controller.lookup\([\'"](?P<name>\w+)[\'"]\)')
CONTROLLER_V1_MACRO = re.compile('^macro Controller: (?P<address>0x[0-9a-fA-F]{1,40})$')
CONTROLLER_INIT = re.compile('^(?P<indent>\s*)self.controller = 0x[0-9A-F]{1,40}')
INDENT = re.compile('^$|^[#\s].*$')

STANDARD_EXTERNS = {
    'controller': 'extern controller: [addToWhitelist:[int256]:int256, assertIsWhitelisted:[int256]:int256, assertOnlySpecifiedCaller:[int256,int256]:_, changeMode:[int256]:int256, emergencyStop:[]:int256, getMode:[]:int256, getOwner:[]:int256, lookup:[int256]:int256, onlyInEmergency:[]:_, release:[]:int256, removeFromWhitelist:[int256,int256]:int256, setValue:[int256,int256]:int256, stopInEmergency:[]:_, suicide:[int256,int256,int256]:int256, switchModeSoOnlyEmergencyStopsAndEscapeHatchesCanBeUsed:[]:_, transferOwnership:[int256,int256,int256,int256]:int256, updateController:[int256,int256]:int256]',
    # ERC20 and aliases used in Augur code
    'ERC20': 'extern ERC20: [allowance:[address,address]:uint256, approve:[address,uint256]:uint256, balanceOf:[address]:uint256, decimals:[]:uint256, name:[]:uint256, symbol:[]:uint256, totalSupply:[]:uint256, transfer:[address,uint256]:uint256, transferFrom:[address,address,uint256]:uint256]',
    'subcurrency': 'extern subcurrency: [allowance:[address,address]:uint256, approve:[address,uint256]:uint256, balanceOf:[address]:uint256, decimals:[]:uint256, name:[]:uint256, symbol:[]:uint256, totalSupply:[]:uint256, transfer:[address,uint256]:uint256, transferFrom:[address,address,uint256]:uint256]',
    'rateContract': 'extern rateContract: [rateFunction:[]:int256]',
    'forkResolveContract': 'extern forkResolveContract: [resolveFork:[int256]:int256]',
    'shareToken': 'extern shareToken: [allowance:[address,address]:int256, approve:[address,uint256]:int256, balanceOf:[address]:int256, changeTokens:[int256,int256]:int256, createShares:[address,uint256]:int256, destroyShares:[address,uint256]:int256, getDecimals:[]:int256, getName:[]:int256, getSymbol:[]:int256, modifySupply:[int256]:int256, setController:[address]:int256, suicideFunds:[address]:_, totalSupply:[]:int256, transfer:[address,uint256]:int256, transferFrom:[address,address,uint256]:int256]',
}

DEFAULT_RPCADDR = 'http://localhost:8545'
DEFAULT_CONTROLLER = '0xDEADBEEF'
VALID_ADDRESS = re.compile('^0x[0-9A-F]{1,40}$')


SERPENT_EXT = '.se'
MACRO_EXT = '.sem'


class LoadContractsError(Exception):
    """Error class for all errors while processing Serpent code."""
    def __init__(self, msg, *format_args, **format_params):
        super(self.__class__, self).__init__(msg.format(*format_args, **format_params))
        if not hasattr(self, 'message'):
            self.message = self.args[0]


class TempDirCopy(object):
    """Makes a temporary copy of a directory and provides a context manager for automatic cleanup."""
    def __init__(self, source_dir):
        self.source_dir = os.path.abspath(source_dir)
        self.temp_dir = tempfile.mkdtemp()
        self.temp_source_dir = os.path.join(self.temp_dir,
                                            os.path.basename(self.source_dir))
        shutil.copytree(self.source_dir, self.temp_source_dir)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        shutil.rmtree(self.temp_dir)
        if not any((exc_type, exc, traceback)):
            return True
        return False

    def find_files(self, extension):
        """Finds all the files ending with the extension in the directory."""
        paths = []
        for directory, subdirs, files in os.walk(self.temp_source_dir):
            for filename in files:
                if filename.endswith(extension):
                    paths.append(os.path.join(directory, filename))

        return paths

    def commit(self, dest_dir):
        """Copies the contents of the temporary directory to the destination."""
        if os.path.exists(dest_dir):
            LoadContractsError(
                'The target path already exists: {}'.format(
                    os.path.abspath(dest_dir)))

        shutil.copytree(self.temp_source_dir, dest_dir)

    def cleanup(self):
        """Deletes the temporary directory."""
        try:
            shutil.rmtree(self.temp_dir)
        except OSError as exc:
            # If ENOENT it raised then the directory was already removed.
            # This error is not harmful so it shouldn't be raised.
            # Anything else is probably bad.
            if exc.errno == errno.ENOENT:
                return False
            else:
                raise
        else:
            return True

    def original_path(self, path):
        """Returns the orignal path which the copy points to."""
        return path.replace(self.temp_source_dir, self.source_dir)


def strip_license(code_lines):
    """Separates the top-of-the-file license stuff from the rest of the code."""
    for i, line in enumerate(code_lines):
        if not line.startswith('#'):
            return code_lines[:i], code_lines[i:]
    return [], code_lines


def strip_imports(code_lines):
    """Separates dependency information from Serpent code in the file."""
    license, code = strip_license(code_lines)
    dependencies = []
    other_code = []

    for i, line in enumerate(code):
        if line.startswith('import'):
            m = IMPORT.match(line)
            if m:
                dependencies.append((m.group(1), m.group(2)))
            else:
                raise LoadContractsError(
                    'Weird import at {line_num}: {line}',
                    line_num=i,
                    line=line)
        else:
            other_code.append(line)

    return license, dependencies, other_code


def path_to_name(path):
    """Extracts the contract name from the path."""
    return os.path.basename(path).replace(SERPENT_EXT, '')


def update_controller(code_lines, controller_addr):
    """Updates the controller address in the code.

    If there is no 'data controller' declaration it is added.
    Similarly, if no controller initialization line is found in
    the init function, then it is added, and if there is no init
    function, one is added.
    """
    code_lines = code_lines[:]

    first_def = None
    data_line = None
    init_def = None
    for i, line in enumerate(code_lines):
        if line == 'data controller':
            data_line = i
        if line.startswith('def init()'):
            init_def = i
        if line.startswith('def') and first_def is None:
            first_def = i

    if first_def is None:
        raise LoadContractsError('No functions found! Is this a macro file?')

    controller_init = '    self.controller = {}'.format(controller_addr)

    if init_def is None:
        # If there's no init function, add it before the first function
        init_def = first_def
        code_lines = code_lines[:init_def] + ['def init():', controller_init, ''] + code_lines[init_def:]
    else:
        # If there is, add the controller init line to the top of the init function
        # and remove any other lines in init that set the value of self.controller
        code_lines.insert(init_def + 1, controller_init)
        i = init_def + 2
        while INDENT.match(code_lines[i]):
            m = CONTROLLER_INIT.match(code_lines[i])
            if m:
                del code_lines[i]
            else:
                i += 1

    if data_line is None:
        # If there's no 'data controller' line, add it before the init.
        code_lines = code_lines[:init_def] + ['data controller', ''] + code_lines[init_def:]

    return code_lines


def imports_to_externs(source_dir, target_dir):
    """Translates code using import syntax to standard Serpent externs."""
    with TempDirCopy(source_dir) as td:
        serpent_paths = td.find_files(SERPENT_EXT)

        contracts = {}

        for path in serpent_paths:
            # TODO: Something besides hard coding this everywhere!!!
            if os.path.basename(path) == 'controller.se':
                continue

            name = path_to_name(path)

            with open(path) as f:
                code_lines = [line.rstrip() for line in f]

            try:
                code_lines = update_controller(code_lines, DEFAULT_CONTROLLER)
                license, dependencies, other_code = strip_imports(code_lines)
            except LoadContractsError as exc:
                raise LoadContractsError(
                    'Caught error while processing {name}: {error}',
                    name=name,
                    error=exc.message)

            info = {'license': license,
                    'dependencies': dependencies,
                    'stripped_code': '\n'.join(other_code)}

            # the stripped code is writen back so the serpent module can handle 'inset' properly
            with open(path, 'w') as f:
                f.write(info['stripped_code'])

            info['signature'] = pretty_signature(path, name)
            info['path'] = path
            contracts[name] = info

        lookup_fmt = '{} = self.controller.lookup(\'{}\')'
        for name in contracts:
            info = contracts[name]
            signatures = ['', STANDARD_EXTERNS['controller'], '']
            for oname, alias in info['dependencies']:
                signatures.append('')
                signatures.append(lookup_fmt.format(alias, oname))
                signatures.append(contracts[oname]['signature'])
            signatures.append('') # blank line between signatures section and rest of code
            new_code = '\n'.join(info['license'] + signatures + [info['stripped_code']])
            path = info['path']

            with open(path, 'w') as f:
                f.write(new_code)

        td.commit(target_dir)


def update_externs(source_dir, controller):
    """Updates all externs in source_dir."""

    with TempDirCopy(source_dir) as td:
        extern_map = STANDARD_EXTERNS.copy()
        serpent_files = td.find_files(SERPENT_EXT)

        for path in serpent_files:
            # TODO: Something besides hard coding this everywhere!!!
            if os.path.basename(path) == 'controller.se':
                continue

            name = path_to_name(path)
            extern_map[name] = pretty_signature(path, name)

        for path in serpent_files:
            # TODO: Something besides hard coding this everywhere!!!
            if os.path.basename(path) == 'controller.se':
                continue

            with open(path) as f:
                code_lines = [line.rstrip() for line in f]

            if controller:
                try:
                    code_lines = update_controller(code_lines, controller)
                except Exception as exc:
                    raise LoadContractsError(
                        'Caught error while processing {path}: {err}',
                        path=td.original_path(path),
                        err=str(exc))

            license, code_lines = strip_license(code_lines)

            for i in range(len(code_lines)):
                line = code_lines[i]
                m = EXTERN.match(line)

                if (line.startswith('extern') and m is None or
                    m and m.group(1) not in extern_map):

                    raise LoadContractsError(
                        'Weird extern at line {line_num} in file {path}: {line}',
                        line_num=(len(license) + i + 1),
                        path=td.original_path(path),
                        line=line)
                elif m:
                    extern_name = m.group(1)
                    code_lines[i]  = extern_map[extern_name]

            code_lines = '\n'.join(license + code_lines)
            with open(path, 'w') as f:
                f.write(code_lines)

        shutil.rmtree(source_dir)
        td.commit(source_dir)


def upgrade_controller(source, controller):
    """Replaces controller macros with an updateable storage value."""
    with TempDirCopy(source) as td:
        serpent_files = td.find_files(SERPENT_EXT)

        for path in serpent_files:
            # TODO: Something besides hard coding this everywhere!!!
            if os.path.basename(path) == 'controller.se':
                continue

            with open(path) as f:
                code_lines = [line.rstrip() for line in f]

            if controller:
                try:
                    code_lines = update_controller(code_lines, controller)
                except LoadContractsError as exc:
                    raise LoadContractsError('Caught error while processing {path}: {err}',
                        path=td.original_path(path),
                        err=exc.message)

            new_code = []
            for i in range(len(code_lines)):
                line = code_lines[i]
                if CONTROLLER_V1_MACRO.match(line):
                    continue # don't include the macro line in the new code
                m = CONTROLLER_V1.match(line)
                if m:
                    new_code.append('{indent}{alias} = self.controller.lookup(\'{name}\')'.format(**m.groupdict()))
                else:
                    new_code.append(line)

            with open(path, 'w') as f:
                f.write('\n'.join(new_code))

        shutil.rmtree(source)
        td.commit(source)


class ContractLoader(object):
    """A class which updates and compiles Serpent code via ethereum.tester.state.

    Examples:
    contracts = ContractLoader('src', 'controller.se', ['mutex.se', 'cash.se', 'repContract.se', 'reputationFaucet.se'])
    print(contracts.foo.echo('lol'))
    print(contracts['bar'].bar())
    contracts.cleanup()
    """
    def __init__(self, source_dir, controller, special):
        self.__state = ethereum.tester.state()
        self.__tester = ethereum.tester
        ethereum.tester.gas_limit = 4200000
        self.__contracts = {}
        self.__temp_dir = TempDirCopy(source_dir)
        try:
            self.__state.block.number += HOMESTEAD_BLOCK_NUMBER # enable DELEGATECALL opcode
        except:
            self.__state.state.block_number += HOMESTEAD_BLOCK_NUMBER # enable DELEGATECALL opcode
        self.__source_dir = source_dir

        serpent_files = self.__temp_dir.find_files(SERPENT_EXT)

        for file in serpent_files:
            if os.path.basename(file) == controller:
                print('Creating controller..')
                self.__contracts['controller'] = self.__state.abi_contract(file)
                controller_addr = '0x' + hexlify(self.__contracts['controller'].address)
                print('Updating externs...')
                update_externs(self.__temp_dir.temp_source_dir, controller_addr)
                print('Finished.')
                self.__state.mine()
                break
        else:
            raise LoadContractsError('Controller not found! {}', controller)

        for contract in special:
            for file in serpent_files:
                if os.path.basename(file) == contract:
                    name = path_to_name(file)
                    print(name)
                    self.__contracts[name] = self.__state.abi_contract(file)
                    address = self.__contracts[name].address
                    self.controller.setValue(name.ljust(32, '\x00'), address)
                    self.controller.addToWhitelist(address)
                    self.__state.mine()
                    print('Contract creation successful:', name)

        for file in serpent_files:
            name = path_to_name(file)

            if name in self.__contracts:
                continue

            try:
                print(name)
                self.__contracts[name] = self.__state.abi_contract(file)
            except Exception as exc:
                with open(file) as f:
                    code = f.read()
                raise LoadContractsError(
                    'Error compiling {name}:\n\n{code}',
                    name=name,
                    code=code)
            else:
                print('Contract creation successful:', name)

            self.controller.setValue(name.ljust(32, '\x00'), self.__contracts[name].address)
            self.controller.addToWhitelist(self.__contracts[name].address)

    def __getattr__(self, name):
        """Use it like a namedtuple!"""
        try:
            return self.__contracts[name]
        except KeyError:
            raise AttributeError()

    def __getitem__(self, name):
        """Use it like a dict!"""
        return self.__contracts[name]

    def cleanup(self):
        """Deletes temporary files."""
        self.__temp_dir.cleanup()

    def __del__(self):
        """ContractLoaders try to clean up after themselves."""
        self.cleanup()

    def recompile(self, name):
        """Gets the latest copy of the code from the source path, recompiles, and updates controller."""
        self.__temp_dir = TempDirCopy(self.__source_dir)
        for file in self.__temp_dir.find_files(SERPENT_EXT):
            if path_to_name(file) == name:
                break

        og_path = self.__temp_dir.original_path(file)
        os.remove(file)
        shutil.copy(og_path, file)
        update_externs(self.__temp_dir.temp_source_dir, self.get_address('controller'))
        self.__contracts[name] = self.__state.abi_contract(file)
        self.controller.setValue(name.ljust(32, '\x00'), self.__contracts[name].address)
        self.controller.addToWhitelist(self.__contracts[name].address)
        self.__state.mine()

    def get_address(self, name):
        """Hex-encoded address of the contract."""
        return '0x' + hexlify(self.__contracts[name].address)


def main():
    parser = argparse.ArgumentParser(
        description='Compiles collections of serpent contracts.',
        epilog='Try a command followed by -h to see it\'s help info.')

    commands = parser.add_subparsers(title='commands')

    translate = commands.add_parser('translate',
                                    help='Translate imports to externs.')
    translate.add_argument('-s', '--source',
                           help='Directory to search for Serpent code.',
                           required=True)
    translate.add_argument('-t', '--target',
                           help='Directory to save translated code in.',
                           required=True)
    translate.set_defaults(command='translate')

    update = commands.add_parser('update',
                                 help='Updates the externs in --source.')
    update.add_argument('-s', '--source',
                        help='Directory to search for Serpent code.',
                        required=True)
    update.add_argument('-c', '--controller',
                        help='The address in hex of the Controller contract.',
                        default=None)
    update.set_defaults(command='update')

    compile_ = commands.add_parser('compile',
                                   help='Compiles and uploads all the contracts in --source. (TODO)')
    compile_.add_argument('-s', '--source',
                          help='Directory to search for Serpent code.',
                          required=True)
    compile_.add_argument('-r', '--rpcaddr',
                          help='Address of RPC server.',
                          default=DEFAULT_RPCADDR)
    compile_.add_argument('-o', '--out',
                          help='Filename for address json.')
    compile_.add_argument('-O', '--overwrite',
                          help='If address json already exists, overwrite.',
                          action='store_true', default=False)
    compile_.set_defaults(command='compile')

    upgrade = commands.add_parser('upgrade', help='Upgrades to the new controller mechanism')
    upgrade.add_argument('-s', '--source', help='Directory to search for Serpent code.', required=True)
    upgrade.add_argument('-c', '--controller', help='Sets the controller address', default=None)
    upgrade.set_defaults(command='upgrade')

    args = parser.parse_args()

    try:
        if not hasattr(args, 'command'):
            parser.print_help()
        elif args.command == 'translate':
            imports_to_externs(args.source, args.target)
        elif args.command ==  'update':
            update_externs(args.source, args.controller)
        elif args.command == 'upgrade':
            upgrade_controller(args.source, args.controller)
        else:
            raise LoadContractsError('command not implemented: {cmd}', cmd=args.command)
    except LoadContractsError as exc:
        print(exc)
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
