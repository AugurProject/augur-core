# Serpent Style Guide

This is a collection of rules to make large Serpent projects easier to work with.

## Source File Organization

* All Serpent contract files should have the extension `.se`, and all Serpent macros should be in their own files with the extension `.sem`.
* The Serpent source tree should contain nothing but Serpent contract and macro files.
* All indentation should be multiples of 4 spaces, not tabs or any other size spaces.

## Code Sections

All Serpent contracts should be organized into the following sections in the following order, whenever each section is neccessary:

1. The license.
2. Macro file insets.
3. externs
4. data declarations
5. global variables
6. functions

Each section should be separated by two blanks lines.

### The License
Each file should start with a comment block containing the relevant license.

### Macro Insets
All macro insets should be placed on consecutive lines, with no comments or blank lines between them.

### The `extern` Section
All externs should be placed on consecutive lines, with no comments or blank lines between them.

### `data` Declarations
The data section may have comments and blank lines in between however the author wishes, except that two consecutive blank lines should not appear within the section.

### Global Variables
This section should follow the same rules as the data section.

### Functions
Serpent has three important special functions: `init`, `shared`, and `any`.
The init function, if any, should appear first in the file, and there must only be one init function in the file. The `shared` function should be next, and then the `any` function if necessary. Care should be taken if using an `any` function and global variables. The Serpent compiler gathers all code in the global variables section together with all code in the `any` function, and executes it all each time the contracts is called. All other functions should go after the special functions. There should be no occurrences of consecutive blank lines in this section, and it should end in a blank line.