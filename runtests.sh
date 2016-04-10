#!/bin/bash
py.test tests/functions --doctest-modules -v
cd src
python python_serpent_test.py
cd ..
