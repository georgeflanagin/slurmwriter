# -*- coding: utf-8 -*-
import typing
from typing import *

"""
These decorators are designed to handle hard errors in operation
and provide a stack unwind and dump.

from urdecorators import show_exceptions_and_frames as trap
# from urdecorators import null_decorator as trap

In production, we can swap the commented line for the one 
preceding it. 

"""

# System imports
import bdb
import contextlib
import datetime
from   functools import wraps
import inspect
import os
import sys
import types

# Credits
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2019, George Flanagin'
__credits__ = 'Based on Github Gist 1148066 by diosmosis'
__version__ = '0.1'
__maintainer__ = 'George Flanagin'
__email__ = 'me@georgeflanagin.com'
__status__ = 'Production'
__license__ = 'MIT'


def null_decorator(o:object) -> object:
    """
    The big nothing.
    """
    return o


def show_exceptions(func:object) -> object:
    """
    A **simple** decorator function to anticipate errors that might
    be created by the compilation process.
    """
    def func_wrapper(*args, **kwargs):
        error_message = ""
        try:
           return func(*args, **kwargs)

        except Exception as e:
            sys.stderr.write(str(e))
            return None

    return func_wrapper



def trap(func:object) -> None:
    """
    An amplified version of the show_exceptions decorator.
    """

    @wraps(func)
    def wrapper(*args, **kwds):
        __wrapper_marker_local__ = None
    
        try:
            return func(*args, **kwds)

        except KeyboardInterrupt as e:
            sys.stderr.write('>>> leaving via control-c')
            sys.exit(os.EX_OK)

        except Exception as e:
            if type(e) == bdb.BdbQuit and os.isatty(0):
                print("Exiting. You asked to stop the debugger.")
                sys.exit(os.EX_OK)

            print("{}".format(e))
            # Who am I?
            pid = 'pid{}'.format(os.getpid())

            # First order of business: create a dump file. The file will be under
            # $CANOE_LOG with today's ISO date string as the dir name.
            new_dir = os.path.join(os.getcwd(), datetime.datetime.today().isoformat()[:10])
            os.makedirs(new_dir, exist_ok=True)

            # The file name will be the pid (possibly plus something like "A" if this
            # is the second time today this pid has failed).
            candidate_name = os.path.join(new_dir, pid)
            
            sys.stderr.write("writing dump to file {}".format(candidate_name))

            with open(candidate_name, 'a') as f:
                with contextlib.redirect_stdout(f):
                    # Protect against further failure -- log the exception.
                    try:
                        e_type, e_val, e_trace = sys.exc_info()
                    except Exception as e:
                        sys.stderr.write(str(e))

                    print('Exception raised {}: "{}"'.format(e_type, e_val))
                    
                    # iterate through the frames in reverse order so we print the
                    # most recent frame first
                    for frame_info in inspect.getinnerframes(e_trace):
                        f_locals = frame_info[0].f_locals
                
                        # if there's a local variable named __wrapper_marker_local__, we assume
                        # the frame is from a call of this function, 'wrapper', and we skip
                        # it. The problem happened before the dumping function was called.
                        if '__wrapper_marker_local__' in f_locals: continue

                        # log the frame information
                        print('\n**File <{}>, line {}, in function {}()\n    {}'.format(
                            frame_info[1], frame_info[2], frame_info[3], frame_info[4][0].lstrip()
                            ))

                        # log every local variable of the frame
                        for k, v in f_locals.items():
                            try:
                                print('    {} = {}'.format(k, v))
                            except:
                                pass

                    print('\n')

        sys.exit(os.EX_DATAERR)

    return wrapper

