#!/usr/bin/env python

import os
from load_contracts import ContractLoader

SRC = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'src')

c = ContractLoader(SRC, 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'])
