#!/usr/bin/env python

import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))

from upload_contracts import ContractLoader

contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
