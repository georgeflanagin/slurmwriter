# -*- coding: utf-8 -*-
import typing
from   typing import *

###
# Standard imports.
###

import os
import sys

import argparse
import math
import platform
import random
import resource
import time

###
# Parts of this project.
###

from   gkfdecorators import show_exceptions_and_frames as trap
import pick

programs={
    
    }

def slurmwriter_main(myargs:argparse.Namespace) -> int:

    return os.EX_OK


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="slurmwriter", 
        description="A program to help newbies write SLURM jobs on Spydur.")

    myargs = parser.parse_args()
    dump_cmdline(myargs)

    sys.exit(slurmwriter_main(myargs))
