# -*- coding: utf-8 -*-
"""
This file contains the data to drive the slurmwriter through the
rules written as navigable branches of the SloppyTree.
"""
import typing
from   typing import *

###
# Standard imports.
###
import os
import os.path
import sys

import datetime
import getpass
import grp
import pwd
import time
# Putting this import first, we can run pip if we need any of the
# packages named in the try-block.
import utils

try:
    import dateparser
except ImportError as e:
    print("This program requires dateparser.")
    if utils.dorunrun('pip3 install dateparser --user'):
        import dateparser
    else:
        sys.exit(os.EX_SOFTWARE)

###
# Other parts of this project.
###
from   sloppytree import SloppyTree

###
# The netid of the user running this instance of the program.
###

mynetid = getpass.getuser()
VERSION = datetime.datetime.fromtimestamp(os.stat(__file__).st_mtime).isoformat()[:16]

###
# These are function to support the boundary checking
# when we collect data from the user. 
###
def mygroups() -> Tuple[str]:
    global mynetid
    
    groups = [g.gr_name for g in grp.getgrall() if mynetid in g.gr_mem]
    primary_group = pwd.getpwnam(mynetid).pw_gid
    groups.append(grp.getgrgid(primary_group).gr_name)
    return tuple(groups)
    

def hours_to_hms(h:float) -> str:
    
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
    

limits = SloppyTree()
limits.max_hours = 96
limits.ram.leftover = 4
limits.cores.leftover = 2

params = SloppyTree()

# These two tuples must be edited for the computer where SLURM is
# being used. There is no obvious way to find the installed software.
params.locations.programs = ('/usr/local/sw', '/opt/sw')
params.locations.modules = ('/usr/local/sw/modules')

# If we cannot find the 'sinfo' program, then this is not a SLURM
# machine, or the current user does not have SLURM utilities in
# the PATH.
params.querytool.opts = '-o "%50P %10c  %10m  %25f  %10G "'
params.querytool.exe = utils.dorunrun("which sinfo", return_datatype=str)
if not params.querytool.exe:
    sys.stderr.write('SLURM does not appear to be on this machine.')
    sys.exit(os.EX_SOFTWARE)


def parse_sinfo() -> SloppyTree:
    """
    Query the current environment to get the description of the
    cluster. Return it as a SloppyTree.
    """
    global params

    # These options give us information about cpus, memory, and
    # gpus on the partitions. The first line of the output
    # is just headers.
    result = utils.dorunrun(
        f"{params.querytool.exe} {params.querytools.opts}", 
        return_datatype=str).split('\n')[1:]

    partitions = ( _[0] for x in result for _ in x.split() )
    cores = zip(partitions, ( _[1] for x in result for _ in x.split() ) )
    memories = zip(partitions, ( _[2] for x in result for _ in x.split() ) )
    xtras = zip(partitions, ( _[3] for x in result for _ in x.split() ) )
    gpus = zip(partitions, ( _[4] for x in result for _ in x.split() ) )

    tree = SloppyTree()
    for k in partitions: tree[k]
    for k, v in cores: tree[k].cores = v
    for k, v in memories: tree[k].ram = v
    for k, v in xtras: tree[k].xtras = v
    for k, v in gpus: tree[k].gpus = v
    
    return tree

# Partitions represent where you want to run the program. It is a n-ary tree,
# where the first layer of keys represents the partitions. Subsequent layers
# are tree-nodes with properties of the partition.
partitions = parse_sinfo()
all_partitions = set(( k for k in partitions ))

# This is a list of condos on Spydur. It will not hurt anything to
# leave the code in place, as the set subtraction will have no effect.
condos = set(('bukach', 'diaz', 'erickson', 'johnson', 'parish', 'yang1', 'yang2', 'yangnolin'))
community_partitions_plenum = all_partitions - condos


# programs contains the user-level concepts about 
programs = SloppyTree()

programs.amber20.desc="biomolecular simulation"
programs.amber20.modules = 'amber/20', 
programs.amber20.partition_choices = ('parish',) + community_partitions_gpu

programs.gaussian.desc="electronic structure modeling"
programs.gaussian.modules = 'gaussian',
programs.gaussian.partition_choices = ('parish',) + community_partitions_compute

###
# Each of the trees is a decision tree for the user. Some notes about the
# elements.
#
#  prompt -- if your dialog element has no prompt, the user will not be
#       queried about it. This allows you to put other elements in the tree.
#       Even when these are just strings, they should be lambda functions
#       because the program logic is print(element()) rather than print(element).
#  default -- also a lambda, and if present provides a value when the
#       user fails to type in anything.
#  datatype -- int, str, float, list, etc. Effectively, these are lambda-s
#       because the program coerces the input to this type from str.
#  constraints -- a tuple of lambda-s to check allowable values.
###

dialog = SloppyTree()

dialog.username.answer = mynetid
dialog.username.groups = mygroups() 

dialog.jobname.prompt = lambda : "Name of your job"
dialog.jobname.datatype = str

dialog.output.prompt = lambda : "Name of your job's output file"
dialog.output.default = lambda : f"{os.getenv('HOME')}/{dialog.jobname.answer}.txt"
dialog.output.datatype = str

dialog.program.prompt = lambda : "What program do you want to run"
dialog.program.default = lambda : ""
dialog.program.datatype = str
dialog.program.constraints = lambda x : not len(x) or x.lower() in programs.keys(),

dialog.partition.prompt = lambda : "Name of the partition where you want to run your job"
dialog.partition.default = lambda : 'basic'
dialog.partition.datatype = str
dialog.partition.constraints = lambda x : x in partitions,

dialog.account.prompt = lambda : f"What account is your user id, {mynetid}, associated with"
dialog.account.default = lambda : f"users"
dialog.account.datatype = str
dialog.account.constraints = lambda x : x in dialog.username.groups,
dialog.account.messages = lambda x : f"{x} is not one of your groups. They are {dialog.username.groups}",

dialog.datadir.prompt = lambda : "Where is your input data directory"
dialog.datadir.default = lambda : f"{os.getenv('HOME')}"
dialog.datadir.datatype = str
dialog.datadir.constraints = lambda x : os.path.exists(x), lambda x : os.access(x, os.R_OK)

dialog.scratchdir.prompt = lambda : "Where is your scratch directory"
dialog.scratchdir.default = lambda : f"{os.getenv('HOME')}/scratch"
dialog.scratchdir.datatype = str
dialog.scratchdir.constraints = (
    lambda x: os.makedirs(x, mode=0o750, exist_ok=True) or True, 
    lambda x : os.path.exists(x), 
    lambda x : os.access(x, os.R_OK|os.W_OK) 
    )

dialog.mem.prompt = lambda : "How much memory (in GB)"
dialog.mem.default = lambda : 16
dialog.mem.datatype = int
dialog.mem.constraints = lambda x : 1 < x < partitions[dialog.partition.answer].ram - limits.ram.leftover, 
dialog.mem.messages = lambda x : f"In {dialog.partition.answer}, \
the maximum amount of memory is {partitions[dialog.partition.answer].ram - limits.ram.leftover}",

dialog.cores.prompt = lambda : "How many cores"
dialog.cores.default = lambda : 8
dialog.cores.datatype = int
dialog.cores.constraints = lambda x : 0 < x < partitions[dialog.partition.answer].cores - limits.cores.leftover,
dialog.cores.messages = lambda x : f"You may ask for a maximum of {partitions[dialog.partition.answer].cores - limits.cores.leftover}\
for jobs in {dialog.partition.answer}.",

dialog.time.prompt = lambda : "How long should this run (in hours)"
dialog.time.default = lambda : 1
dialog.time.datatype = float
dialog.time.constraints = lambda x : x < limits.max_hours,
dialog.time.reformat = lambda x : hours_to_hms(x)
dialog.time.messages = lambda x : f"The maximum run time is {limits.max_hours}."

dialog.start.prompt = lambda : "When do you want the job to run"
dialog.start.default = lambda : "now"
dialog.start.datatype = str
dialog.start.constraints = lambda x : x in ('now', 'today', 'tomorrow') or time_check(x),
dialog.start.reformat = lambda x : time_check(x, True)

dialog.jobfile.prompt = lambda : "What will be the name of this new jobfile"
dialog.jobfile.default = lambda : f"{os.getenv('OLDPWD')}/{dialog.jobname.answer}.slurm"
dialog.jobfile.datatype = str
dialog.jobfile.constraints = lambda x : os.access(os.path.dirname(x), os.W_OK),
dialog.jobfile.messages = lambda x : f"Either {x} doesn't exist, or you cannot write to it.",

# This is the catch all message if we cannot tell the user something
# more specific.
for k in ( _ for _ in dialog if 'prompt' in _):
    if 'messages' not in dialog[k]:
        dialog[k].messages = lambda x : f"The value you supplied, {x}, cannot be used here.",
