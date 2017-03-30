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

if (3, 0) <= sys.version_info:
	_old_mk_signature = serpent.mk_signature
	def mk_signature(code):
		return _old_mk_signature(code).decode()
	serpent.mk_signature = mk_signature

PYNAME = '[A-Za-z_][A-Za-z0-9_]*'
IMPORT = re.compile('import ({0}) as ({0})'.format(PYNAME))

DEFAULT_RPCADDR = 'http://localhost:8545'
DEFAULT_SRCDIR = './src'
DEFAULT_BUILDDIR = './build'

SERPENT_EXT = '.se'
MACRO_EXT = '.sem'

parser = argparse.ArgumentParser(description='Compiles collections of serpent contracts.')
parser.add_argument('-R', '--rpcaddr', help='Address of RPC server', default=DEFAULT_RPCADDR)
parser.add_argument('-S', '--srcdir', help='Directory to search for Serpent code', default=DEFAULT_SRCDIR)
parser.add_argument('-B', '--builddir', help='Directory to save translated code in.', default=DEFAULT_BUILDDIR)
modes = parser.add_mutually_exclusive_group(required=True)
modes.add_argument('-T', '--translate', help='Just translate imports and save in builddir', action='store_true', default=False)
modes.add_argument('-U', '--update', help='Updates the externs in all the contracts.', action='store_true', default=False)


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


def strip_dependencies(serpent_file):
	"""Separates dependency information from Serpent code in the file."""
	dependencies = []
	other_code = []
	crud = []
	done_with_crud = False
	with open(serpent_file) as code:
		for i, line in enumerate(code):
			line = line.rstrip()
			if line.startswith('#') and not done_with_crud:
				crud.append(line)
				continue
			done_with_crud = True

			if line.startswith('import'):
				m = IMPORT.match(line)
				if m is None:
					print('SAD! weird import at line', i, 'in contract', path)
					sys.exit(1)
				dependencies.append((m.group(1), m.group(2)))
			else:
				other_code.append(line)

	other_code.append('')
	crud.append('')

	return dependencies, '\n'.join(other_code), '\n'.join(crud)


def imports_to_externs(source_dir, new_dir):
	"""Translates code using import syntax to standard Serpent externs."""
	source_dir = os.path.abspath(source_dir)
	new_dir = os.path.abspath(new_dir)

	shutil.copytree(source_dir, new_dir)

	serpent_files = find_files(new_dir, SERPENT_EXT)

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
		signatures = ['macro Controller: 0xC001D00D', 'extern Controller: [lookup:[int256]:int256, checkWhitelist:[int256]:int256]']
		for oname, alias in info['dependencies']:
			signatures.append('')
			signatures.append(lookup_fmt.format(alias, oname))
			signatures.append(source_map[oname]['signature'])
		signatures.append('')
		new_code = '\n'.join([info['crud']] + signatures + [info['stripped_code']])
		path = info['path']

		with open(path, 'w') as f:
			f.write(new_code)


def update_externs(source_dir):
	pass


def main():
	args = parser.parse_args()

	if args.translate:
		imports_to_externs(args.srcdir, args.builddir)
	elif args.update:
		update_externs(args.srcdir)
	else:
		return 1

	return 0

if __name__ == '__main__':
	sys.exit(main())
