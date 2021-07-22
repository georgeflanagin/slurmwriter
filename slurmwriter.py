# -*- coding: utf-8 -*-
"""Slurmwriter is a simple program to help new SLURM users format
their first jobs properly. A SLURM job can be a little tedious
to construct, and by answering a few questions, this utility
can help you get the basics correct the first time. 
"""

import typing
from   typing import *

min_py = (3, 8)

###
# Standard imports.
###

import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)


# Credits
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2021'
__credits__ = None
__version__ = str(math.pi**2)[:5]
__maintainer__ = 'George Flanagin'
__email__ = ['me+ur@georgeflanagin.com', 'gflanagin@richmond.edu']
__status__ = 'Teaching example'
__license__ = 'MIT'

import argparse
import getpass

###
# Parts of this project.
###

from   gkfdecorators import trap
from   data import dialog
from   sloppytree import SloppyTree
from   slurmscript import slurmscript

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
    Walk the nodes of the tree to collect information
    from the user, interactively.
    """
    for k in t:
        # Ensure this is a user-prompt element of t.
        if 'prompt' not in t[k]: continue

        complete = False
        while not complete:
            # Step 1: Convert the user's response to the right type.
            x = input(format_prompt(t[k])) 
            x = x if x else t[k].default()
            try:
                x = t[k].datatype(x)
                complete = True

            except ValueError as e:
                print(f"Woops! {x} should be of type {t[k].datatype}")

            except KeyError as e:
                complete = True

            # Step 2: Check the constraints.
            complete = ( complete and 
                'choices' not in t[k] or 
                all (choice(x) for choice in t[k].choices))
            if not complete:
                print(f"Your answer, {x}, is outside the range of allowed values.")    

            # Step 3: Check for reformatting.
            if 'reformat' in t[k]:
                x = t[k].reformat(x)
            
        t[k].answer = x

    return t


@trap
def review_answers(t:SloppyTree) -> bool:
    print("\n----------------------\n")
    for k in t:
        if "prompt" in t[k]:
            print(f"{t[k].prompt()} => {t[k].answer}")

    return truthy(input("\nThese are the answers you provided. Are they OK? [y] : "))
    

@trap
def slurmwriter_main(myargs:argparse.Namespace) -> int:
    global dialog

    print(f"{__doc__}")

    info = SloppyTree()
    info = get_answers(dialog)
    if not review_answers(info): 
        print("OK. Try again.")
        sys.exit(os.EX_DATAERR)

    
    print(f"Writing file {info.jobfile.answer}...")
    code = slurmscript(info)
    with open(info.jobfile.answer, 'w+') as f:
        f.write(code)

    return os.EX_OK


def truthy(text:str) -> bool:
    """
    Deal with all the various ways people represent the truth.
    """
    return text.lower() in ('y', 'yes', 'true', 'ok', '1', '')


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="slurmwriter", 
        description="A program to help newbies write SLURM jobs on Spydur.")

    myargs = parser.parse_args()
    dump_cmdline(myargs)

    try:
        sys.exit(slurmwriter_main(myargs))
    except KeyboardInterrupt as e:
        print("You have asked to exit via control-C")
        sys.exit(os.EX_OK)
