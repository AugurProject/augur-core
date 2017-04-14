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
import errno
import re
from binascii import hexlify
import shutil
import sys
from serpent import mk_signature
import tempfile
import warnings

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

PYNAME = '[A-Za-z_][A-Za-z0-9_]*'
IMPORT = re.compile('import ({0}) as ({0})'.format(PYNAME))
EXTERN = re.compile('extern ({}): .+'.format(PYNAME))

STANDARD_EXTERNS = {
    'controller': 'extern controller: [lookup:[int256]:int256, checkWhitelist:[int256]:int256]',

    # ERC20 and aliases used in Augur code
    'ERC20': 'extern ERC20: [allowance:[uint256,uint256]:uint256, approve:[uint256,uint256]:uint256, balance:[]:uint256, balanceOf:[uint256]:uint256, transfer:[uint256,uint256]:uint256, transferFrom:[uint256,uint256,uint256]:uint256]',
    'subcurrency': 'extern subcurrency: [allowance:[uint256,uint256]:uint256, approve:[uint256,uint256]:uint256, balance:[]:uint256, balanceOf:[uint256]:uint256, transfer:[uint256,uint256]:uint256, transferFrom:[uint256,uint256,uint256]:uint256]',
}

DEFAULT_RPCADDR = 'http://localhost:8545'
DEFAULT_CONTROLLER = '0xDEADBEEF'
CONTROLLER_PATTERN = re.compile('^\s{4}self.controller\s?=\s?(0x[0-9a-fA-F]+)$')
ADDRESS_HEX = re.compile('^0x([0-9A-F]{1,40}|[0-9a-f]{1,40})$')


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
                                            os.path.basename(source_dir))

    def __enter__(self):
        shutil.copytree(self.source_dir, self.temp_source_dir)
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


def is_not_indented(line):
    """True if a line starts with a space of tab."""
    return not (line.startswith(' ') or line.startswith('\t'))


def find_init(code_lines):
    """Finds the line bounds of a Serpent init function."""

    # If there are multiple init functions, the Serpent
    # compiler will silently drop all but the last, and
    # only compile the last. That's bad! >:(

    init_bounds = []
    start = None
    
    for i, line in enumerate(code_lines):
        if line.startswith('def init():'):
            start = i
        elif start is not None and is_not_indented(line):
            init_bounds.append((start, i))
            start = None
        else:
            continue

    if start and not init_bounds:
        return [(start, -1)]

    if not init_bounds:
        return [(None, None)]

    return init_bounds


def update_controller(code_lines, controller_addr):
    """Updates the controller address in the code.

    If there is no 'data controller' declaration it is added.
    Similarly, if no controller initialization line is found in
    the init function, then it is added, and if there is no init
    function, one is added.
    """
    if not ADDRESS_HEX.match(controller_addr):
        raise LoadContractsError('Controller address invalid! {}', controller_addr)

    code_lines = code_lines[:]

    for i in range(len(code_lines)):
        line = code_lines[i]
        if line == 'data controller':
            break
    else:
        code_lines = ['data controller', ''] + code_lines

    init_bounds = find_init(code_lines)

    if len(init_bounds) > 1:
        raise LoadContractsError('Multiple init functions!')

    init_start, init_stop = init_bounds[0]

    controller_line = '    self.controller = {}'.format(controller_addr)

    if init_stop == -1:
        raise LoadContractsError('Weird init function at line {line}!', line=init_start)

    if init_start is None:
        # Augur code follows a convention where data declarations are
        # followed by a comment block describing the declaration's meaning.
        # The blocks are immediately followed by the declaration. data
        # declarations may have a blank line afterward.
        last_data = None
        for i in range(len(code_lines)):
            line = code_lines[i]
            if line.startswith('data'):
                last_data = i
            if line.startswith('#') or line == '':
                continue
            if i > last_data:
                break

        return code_lines[:i] + ['def init():', '', controller_line, ''] + code_lines[i:]

    for i in range(init_start, init_stop):
        line = code_lines[i]
        m = CONTROLLER_PATTERN.match(line)
        if m:
            code_lines[i] = controller_line
            return code_lines
    else:
        code_lines.insert(init_stop, controller_line)
        return code_lines

def imports_to_externs(source_dir, target_dir):
    """Translates code using import syntax to standard Serpent externs."""
    with TempDirCopy(source_dir) as td:
        serpent_paths = td.find_files(SERPENT_EXT)

        contracts = {}

        for path in serpent_paths:
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
            name = path_to_name(path)
            extern_map[name] = pretty_signature(path, name)

        for path in serpent_files:
            with open(path) as f:
                code_lines = [line.rstrip() for line in f]

            license, code_lines = strip_license(code_lines)

            if controller:
                code_lines = update_controller(code_lines, controller)

            for i in range(len(code_lines)):
                line = code_lines[i]
                m = EXTERN.match(line)

                if (line.startswith('extern') and m is None or 
                    m and m.group(1) not in extern_map):

                    raise LoadContractsError(
                        'Weird extern at line {line_num} in file {path}: {line}',
                        line_num=(len(license) + i),
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


class ContractLoader(object):
    pass


def main():
    parser = argparse.ArgumentParser(
        description='Compiles collections of serpent contracts.',
        epilog='Try a command followed by -h to see it\'s help info.')
    parser.set_defaults(command=None)

    commands = parser.add_subparsers(title='commands')

    translate = commands.add_parser('translate',
                                    help='Translate imports to externs.')
    translate.add_argument('-s', '--source',
                           help='Directory to search for Serpent code',
                           required=True)
    translate.add_argument('-t', '--target',
                           help='Directory to save translated code in.',
                           required=True)
    translate.set_defaults(command='translate')

    update = commands.add_parser('update',
                                 help='Updates the externs in --source.')
    update.add_argument('-s', '--source',
                        help='Directory to search for Serpent code',
                        required=True)
    update.add_argument('-c', '--controller',
                        help='The address in hex of the Controller contract.',
                        default=None)
    update.set_defaults(command='update')

    compile_ = commands.add_parser('compile',
                                   help='Compiles and uploads all the contracts in --source. (TODO)')
    compile_.add_argument('-s', '--source',
                          help='Directory to search for Serpent code',
                          required=True)
    compile_.add_argument('-r', '--rpcaddr',
                          help='Address of RPC server',
                          default=DEFAULT_RPCADDR)
    compile_.add_argument('-o', '--out',
                          help='Filename for address json.')
    compile_.add_argument('-O', '--overwrite',
                          help='If address json already exists, overwrite',
                          action='store_true', default=False)
    compile_.set_defaults(command='compile')

    args = parser.parse_args()

    try:
        if args.command is None:
            parser.print_help()
        elif args.command == 'translate':
            imports_to_externs(args.source, args.target)
        elif args.command ==  'update':
            update_externs(args.source, args.controller)
        else:
            raise LoadContractsError('command not implemented: {cmd}', cmd=args.command)
    except Exception as exc:
        if hasattr(exc, 'message'):
            print(exc.message)
        elif len(exc.args) == 1:
            print(exc.args[0])
        else:
            print(exc.args)
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
