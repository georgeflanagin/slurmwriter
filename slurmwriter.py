# -*- coding: utf-8 -*-
"""Slurmwriter is a simple program to help new SLURM users format
their first jobs properly. A SLURM job can be a little tedious
to construct, and by answering a few questions, this utility
can help you get the basics correct the first time. 
"""

import typing
from   typing import *

###
# Standard imports.
###

import os
import sys

import argparse
import getpass
import math
import platform
import random
import resource
import time

###
# Parts of this project.
###

from   gkfdecorators import trap
from   data import dialog, partitions, programs
from   sloppytree import SloppyTree
from   slurmscript import slurmscript

me = lambda : getpass.getuser()

@trap
def dump_cmdline(args:argparse.ArgumentParser, return_it:bool=False) -> str:
    """
    Print the command line arguments as they would have been if the user
    had specified every possible one (including optionals and defaults).
    """
    if not return_it: print("")
    opt_string = ""
    for _ in sorted(vars(args).items()):
        opt_string += " --"+ _[0].replace("_","-") + " " + str(_[1])
    if not return_it: print(opt_string + "\n", file=sys.stderr)

    return opt_string if return_it else ""


@trap
def format_prompt(t:SloppyTree) -> str:
    """
    Based on the prompt string and optional default value
    to collect data for the "t" node in the tree, build a
    uniform prompt string.
    """
    if 'default' in t:
        d_str = f"[{t.default()}] "
    else:
        t.default = ""
        d_str = ""

    return f"{t.prompt()} {d_str}: " 


@trap
def get_answers(t:SloppyTree) -> SloppyTree:
    """
    Walk the top level nodes of the tree to collect information
    from the user, interactively.
    """
    for k in t:
        if 'prompt' not in t[k]: continue
        x = input(format_prompt(t[k])) 
        t[k].answer = x if x else t[k].default()

    return t


@trap
def review_answers(t:SloppyTree) -> bool:
    print("\n----------------------\n")
    for k in t:
        if "prompt" in t[k]:
            print(f"{t[k].prompt()} => {t[k].answer}")

    result = truthy(input("\nThese are the answers you provided. Are they OK? [y] : "))
    return result
    

@trap
def slurmwriter_main(myargs:argparse.Namespace) -> int:
    global dialog

    print(f"{__doc__}")

    info = SloppyTree()
    info = get_answers(dialog)

    code = slurmscript(info)
    print(f"Writing file {info.jobfile.answer}...")
    with open(info.jobfile.answer, 'w+') as f:
        f.write(code)

    return os.EX_OK


def truthy(text:str) -> bool:
    """
    Deal with all the various ways people represent the truth.
    """
    return text.lower() in ('yes', 'true', 'ok', '1', '')


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="slurmwriter", 
        description="A program to help newbies write SLURM jobs on Spydur.")

    myargs = parser.parse_args()
    dump_cmdline(myargs)

    sys.exit(slurmwriter_main(myargs))
