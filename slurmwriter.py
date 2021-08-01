# -*- coding: utf-8 -*-
"""
Slurmwriter is a simple program to help new SLURM users format
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

import math

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
import datetime
import getpass
import inspect

###
# Parts of this project.
###

from   gkfdecorators import trap
import rules
from   rules import dialog
from   sloppytree import SloppyTree
from   slurmscript import slurmscript
import utils

###
# Useful constants.
###

LAMBDA = lambda:0
OCTOTHORPE = '#'
INTERACTIVE = not utils.script_driven()
VERSION = datetime.datetime.fromtimestamp(os.stat(__file__).st_mtime).isoformat()[:16]

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
def dump_lambdas(o:Any) -> None:
    """
    Print the text of the otherwise invisible lambdas.
    """
    if not isinstance(o, Iterable): o = o, 
    for i, it in enumerate(o):
        if isinstance(it, type(LAMBDA)) and it.__name__ == LAMBDA.__name__:
            print(f"{i}: {inspect.getsource(it)=}")
    

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
def get_answers(t:SloppyTree, myargs:argparse.Namespace) -> SloppyTree:
    """
    Walk the nodes of the tree to collect information
    from the user, interactively. Perform checks for
    each input if any checks exist.
    """
    global INTERACTIVE

    # Ensure this is a user-prompt element of t. Other data in
    # t have no prompt element. 
    for k in ( _ for _ in t if 'prompt' in t[_]):

        complete = False
        while not complete:
            # Convert the user's response to the right type.
            x = scrub_input(format_prompt(t[k])) 
            x = x if x else t[k].default()
            try:
                x = t[k].datatype(x)
                complete = True

            # Not convertable to the give type.
            except ValueError as e:
                print(f"Woops! {x} should be of type {t[k].datatype}")
                if not INTERACTIVE: sys.exit(os.EX_DATAERR)
                continue
                
            # No type coercion rule present.
            except KeyError as e:
                complete = True

            # Step 2: Check the constraints.

            myargs.debug and dump_lambdas(t[k].constraints)
            
            ###
            # Explanation for the following statement:
            #   complete if ( if we passed the type check AND
            #    there are *no* constraints to consider OR
            #    all choice functions return true )
            ###
            complete = ( complete and 
                'constraints' not in t[k] or all (constraint(x) for constraint in t[k].constraints)
                )

            ###
            # Execute the message-rules to help the user get it right next time.
            ###
            if not complete:
                for message in t[k].messages: message(x)
                if not INTERACTIVE: sys.exit(os.EX_DATAERR)
                continue

            # Check for reformatting (mainly the case for timestamps)
            if 'reformat' in t[k]:
                x = t[k].reformat(x)
            
        # Success.
        t[k].answer = x

    return t


def review_answers(t:SloppyTree) -> bool:
    print("\n----------------------\n")
    for k in t:
        if "prompt" in t[k]:
            print(f"{t[k].prompt()} => {t[k].answer}")

    return truthy(input("\nThese are the answers you provided. Are they OK? [y] : "))
    

def scrub_input(prompt_text:str) -> str:
    """
    Like input, but ditches everything after the octothorpe.
    """
    global INTERACTIVE, OCTOTHORPE
    try:
        result = input(prompt_text if INTERACTIVE else "").split(OCTOTHORPE)[0].strip()

    except EOFError as e:
        # In case this is being scripted, and the script ended abruptly.
        sys.exit(os.EX_NOINPUT)

    except KeyboardInterrupt as e:
        sys.exit(os.EX_OK)

    if result=='EOF': sys.exit(os.EX_OK)
    return result
 

def truthy(text:str) -> bool:
    """
    Deal with all the various ways people represent the truth.
    """
    return text.lower() in ('y', 'yes', 't', 'true', 'ok', '1', '')


@trap
def slurmwriter_main(myargs:argparse.Namespace) -> int:
    global dialog, INTERACTIVE, VERSION

    if INTERACTIVE:
        print(f"slurmwriter. Version of {VERSION}")
        print(f"      rules. Version of {rules.VERSION}")
        print(__doc__)

    while True:

        info = SloppyTree()
        info = get_answers(dialog, myargs)
        if INTERACTIVE and not review_answers(info): 
            print("OK. Try again.")
            sys.exit(os.EX_DATAERR)

        
        INTERACTIVE and print(f"Writing file {info.jobfile.answer}...")
        code = slurmscript(info)
        with open(info.jobfile.answer, 'w+') as f:
            f.write(code)

        if INTERACTIVE: break

    return os.EX_OK


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="slurmwriter", 
        description="A program to help newbies write SLURM jobs on Spydur.")

    parser.add_argument('--debug', action='store_true')

    myargs = parser.parse_args()

    try:
        sys.exit(slurmwriter_main(myargs))
    except KeyboardInterrupt as e:
        print("You have asked to exit via control-C")
        sys.exit(os.EX_OK)
