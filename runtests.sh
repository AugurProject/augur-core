#!/bin/bash
python tests/serpent_tests/array_delete_test.py
python tests/serpent_tests/save_load_tests.py
py.test tests/accounts.py --doctest-modules -v
