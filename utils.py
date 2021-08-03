# -*- coding: utf-8 -*-
"""
This file contains conveniences for our slurm development efforts.
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

import datetime
import fnmatch
import getpass
import grp
import math
import pwd
import socket
import stat
import subprocess

# Credits
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2021'
__credits__ = None
__version__ = str(math.pi**2)[:5]
__maintainer__ = 'George Flanagin'
__email__ = ['me+ur@georgeflanagin.com', 'gflanagin@richmond.edu']
__status__ = 'Teaching example'
__license__ = 'MIT'

from   sloppytree import SloppyTree

def all_files_in(s:str, 
    ignore_hidden:bool=True) -> str:
    """
    A generator to cough up the full file names for every
    file in a directory.
    """
    global HIDDENFILES

    s = expandall(s)
    for c, d, files in os.walk(s):
        for f in files:
            fullname = os.path.join(c, f)
            if ignore_hidden and "/." in fullname: 
                pass
            else:
                yield fullname


def all_files_like(dir_to_search:str, 
    fname_pattern:str,
    ignore_hidden:bool=True) -> str:
    """
    A generator to find all the files in dir_to_search 
    that match fname_pattern.
    """
    for f in all_files_in(dir_to_search, ignore_hidden):
        if fnmatch.fnmatch(f, fname_pattern):
            yield f
        else:
            continue


def all_files_of_type(dir_to_search:str, 
    file_type:str,
    ignore_hidden:bool=True) -> str:
    """
    A generator to get the file names of a particular type.
    The types are shown in the filetypes dict.
    """
    for f in all_files_in(dir_to_search, ignore_hidden):
        if get_file_type(f) == file_type.upper():
            yield f
        else:
            continue


def all_module_files() -> str:
    """
    This generator locates all module files that are located in
    the directories that are members of MODULEPATH.
    """
    for location in os.getenv('MODULEPATH', "").split(':'):
        for f in all_files_of_type(location, 'mod'):
            yield f


def dorunrun(command:Union[str, list],
    timeout:int=None,
    verbose:bool=False,
    quiet:bool=False,
    return_datatype:type=bool
    ) -> tuple:
    """
    A wrapper around (almost) all the complexities of running child 
        processes.
    command -- a string, or a list of strings, that constitute the
        commonsense definition of the command to be attemped. 
    timeout -- generally, we don't
    verbose -- do we want some narrative to stderr?
    quiet -- overrides verbose, shell, etc. 
    return_datatype -- this argument corresponds to the item 
        the caller wants returned.
            bool : True if the subprocess exited with code 0.
            int  : the exit code itself.
            str  : the stdout of the child process.

    returns -- a tuple of values corresponding to the requested info.
    """

    if verbose: sys.stderr.write(f"{command=}\n")

    if isinstance(command, (list, tuple)):
        command = [str(_) for _ in command]
        shell = False

    elif isinstance(command, str):
        shell = True

    else:
        raise Exception(f"Bad argument type to dorunrun: {command}")

    r = None
    try:
        result = subprocess.run(command, 
            timeout=timeout, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            shell=shell)

        code = result.returncode
        if return_datatype is bool:
            return code == 0
        elif return_datatype is int:
            return code
        elif return_datatype is str:
            return result.stdout
        elif return_datatype is tuple:
            return code, result.stdout, result.stderr
        elif return_datatype is dict:
            return {"code":code, "stdout":result.stdout, "stderr":result.stderr}
        else:
            raise Exception(f"Unknown: {return_datatype=}")
        
    except subprocess.TimeoutExpired as e:
        raise Exception(f"Process exceeded time limit at {e.timeout} seconds.")    

    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


def expandall(s:str) -> str:
    """
    Expand all the user vars into an absolute path name. If the
    argument happens to be None, it is OK.
    """
    return ( "" if s is None 
        else os.path.abspath(os.path.expandvars(os.path.expanduser(s))))


filetypes = {
    b"%PDF-1." : "PDF",
    b"#%Module" : "MOD",
    b"BZh91A" : "BZ2",
    bytes.fromhex("FF454C46") : "ELF",
    bytes.fromhex("1F8B") : "GZIP",
    bytes.fromhex("FD377A585A00") : "XZ",
    bytes.fromhex("504B0304") : "ZIP",
    bytes.fromhex("504B0708") : "ZIP"
    }


def get_file_type(path:str) -> str:
    """
    By inspection, return the presumed type of the file located 
    at path. Returns a three of four char file type, or None if
    the type cannot be determined. This might be because the
    type cannot be determined when inspected, or because it cannot 
    be opened. 
    """
    global filetypes
    
    try:
        with open(expandall(path), 'rb') as f:
            shred = f.read(256)
    except FileNotFoundError as e:
        # Broken link
        return None

    except PermissionError as e:
        # We have execute on the directory, but not read on the file within.
        return None

    for k, v in filetypes.items():
        if shred.startswith(k): return v

    return "TXT" if shred.isascii() else None
    
    
def hms_to_hours(hms:str) -> float:
    """
    Convert a slurm time like 2-12:00:00 to 
    a number of hours.
    """

    try:
        h, m, s = hms.split(':')
    except Exception as e:
        if hms == 'infinite': return 365*24
        return 0

    try:
        d, h = h.split('-')
    except Exception as e:
        d = 0

    return int(d)*24 + int(h) + int(m)/60 + int(s)/3600


def hours_to_hms(h:float) -> str:
    """
    Convert a number of hours to "SLURM time."
    """
    
    days = int(h / 24)
    h -= days * 24
    hours = int(h)
    h -= hours 
    minutes = int(h * 60)
    h -= minutes/60
    seconds = int(h*60)

    return ( f"{hours:02}:{minutes:02}:{seconds:02}" 
        if h < 24 else 
        f"{days}-{hours:02}:{minutes:02}:{seconds:02}" )


def mygroups() -> Tuple[str]:
    """
    Collect the group information for the current user, including
    the self associated group, if any.
    """
    mynetid = getpass.getuser()
    
    groups = [g.gr_name for g in grp.getgrall() if mynetid in g.gr_mem]
    primary_group = pwd.getpwnam(mynetid).pw_gid
    groups.append(grp.getgrgid(primary_group).gr_name)
    return tuple(groups)
    

def parse_sinfo(params:SloppyTree) -> SloppyTree:
    """
    Query the current environment to get the description of the
    cluster. Return it as a SloppyTree.
    """

    # These options give us information about cpus, memory, and
    # gpus on the partitions. The first line of the output
    # is just headers.
    cmdline = f"{params.querytool.exe} {params.querytool.opts}"
    result = dorunrun( cmdline, return_datatype=str).split('\n')[1:]

    partitions = []
    cores = []
    memories = []
    xtras = []
    gpus = []
    times = []

    # Ignore any blank lines.
    for line in ( _ for _ in result if _):
        f1, f2, f3, f4, f5, f6 = line.split()
        partitions.append(f1)
        cores.append(f2)
        memories.append(f3)
        xtras.append(f4)
        gpus.append(f5)
        times.append(f6)
        
    cores = dict(zip(partitions, cores))
    memories = dict(zip(partitions, memories))
    xtras = dict(zip(partitions, xtras))
    gpus = dict(zip(partitions, gpus))
    times = dict(zip(partitions, times))

    tree = SloppyTree()

    for k, v in cores.items(): tree[k].cores = int(v)
    for k, v in memories.items(): 
        v = "".join(_ for _ in v if _.isdigit())
        tree[k].ram = int(int(v)/1000)
    for k, v in xtras.items(): tree[k].xtras = v if 'null' not in v.lower() else None
    for k, v in gpus.items(): tree[k].gpus = v if 'null' not in v.lower() else None
    for k, v in times.items(): tree[k].max_hours = 24*365 if v == 'infinite' else utils.hms_to_hours(v)

    return tree


def script_driven() -> bool:
    """
    returns True if the input is piped or coming from an IO redirect.
    """

    mode = os.fstat(0).st_mode
    return True if stat.S_ISFIFO(mode) or stat.S_ISREG(mode) else False


def time_check(s:str, return_str:bool=False) -> Union[str, bool]:
    """
    This function either checks or formats the time.

    s -- some string thought to represent a time of day.
    return_str -- a flag, that when True returns the parsed and formatted time.
        If this flag is False, then we just check if the time is valid.
    """
    if return_str:
        return datetime.datetime.isoformat(dateparser.parse(s))[:16]
    else:
        return True if dateparser.parse(s) else False
    

