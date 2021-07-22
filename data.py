# -*- coding: utf-8 -*-
"""
This file contains the data to drive the slurmwriter.
"""

import typing
from   typing import *

###
# Standard imports.
###

import os
import os.path
import sys

try:
    import dateparser
except ImportError as e:
    print("This program requires dateparser.")
    sys.exit(os.EX_SOFTWARE)

import datetime
import getpass
import time

###
# Parts of this project.
###

from   sloppytree import SloppyTree

###
# The netid of the user running this instance of the program.
###

me = lambda : getpass.getuser()
mynetid = getpass.getuser()

###
# These are limits and constraints for some of the boundary checking
# when we collect data from the user. 
###

max_hours = 72



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


def time_check(s:str, return_str:bool=False) -> bool:
    if return_str:
        return datetime.datetime.isoformat(dateparser.parse("now"))[:16]
    else:
        return True if dateparser.parse(s) else False
    

community_partitions_compute = ('basic', 'medium', 'large')
community_partitions_gpu = ('ML', 'sci')
community_partitions_plenum = community_partitions_compute + community_partitions_gpu
condos = ('bukach', 'diaz', 'erickson', 'johnson', 'parish', 'yang1', 'yang2', 'yangnolin')

# partitions represent where you want to run the program
partitions = SloppyTree()

partitions.basic.ram=384
partitions.medium.ram=768
partitions.large.ram=1536
partitions.ML.ram=384
partitions.ML.gpu.type ="A100"
partitions.ML.gpu.count=2
partitions.sci.ram=384
partitions.sci.gpu.type="A40"
partitions.sci.gpu.count=8


partitions.bukach.ram=384
partitions.diaz.ram=1536
partitions.erickson.ram=768
partitions.johnson.ram=384
partitions.parish.ram=768
partitions.yang1.ram=1536
partitions.yang2.ram=384
partitions.yangnolin.ram=384

for k in partitions: partitions[k].cores=52

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
#  choices -- a tuple of lambda-s to check allowable values.
###

dialog = SloppyTree()

dialog.username.answer = mynetid

dialog.jobname.prompt = lambda : "Name of your job"
dialog.jobname.datatype = str

dialog.output.prompt = lambda : "Name of your job's output file"
dialog.output.default = lambda : f"{os.getenv('HOME')}/{dialog.jobname.answer}.txt"
dialog.output.datatype = str

dialog.program.prompt = lambda : "What program do you want to run"
dialog.program.default = lambda : ""
dialog.program.datatype = str
dialog.program.choices = lambda x : not len(x) or x.lower() in programs.keys(),

dialog.partition.prompt = lambda : "Name of the partition where you want to run your job"
dialog.partition.default = lambda : 'basic'
dialog.partition.datatype = str
dialog.partition.choices = lambda x : x in partitions.keys(),

dialog.account.prompt = lambda : f"What account is your user id, {mynetid}, associated with"
dialog.account.default = lambda : f"ur-community"
dialog.account.datatype = str

dialog.datadir.prompt = lambda : "Where is your input data directory"
dialog.datadir.default = lambda : f"{os.getenv('HOME')}"
dialog.datadir.datatype = str
dialog.datadir.choices = lambda x : os.path.exists(x), lambda x : os.access(x, os.R_OK)

dialog.scratchdir.prompt = lambda : "Where is your scratch directory"
dialog.scratchdir.default = lambda : f"/scratch/{mynetid}"
dialog.scratchdir.datatype = str
dialog.scratchdir.choices = lambda x : os.path.exists(x), lambda x : os.access(x, os.R_OK)

dialog.mem.prompt = lambda : "How much memory (in GB)"
dialog.mem.default = lambda : 16
dialog.mem.datatype = int
dialog.mem.choices = lambda x : 1 < x < partitions[dialog.partition.answer].ram - 7, 

dialog.cores.prompt = lambda : "How many cores"
dialog.cores.default = lambda : 8
dialog.cores.datatype = int
dialog.cores.choices = lambda x : 0 < x < partitions[dialog.partition.answer].cores - 1,

dialog.time.prompt = lambda : "How long should this run (in hours)"
dialog.time.default = lambda : 1
dialog.time.datatype = float
dialog.time.choices = lambda x : x < max_hours,
dialog.time.reformat = lambda x : hours_to_hms(x)

dialog.start.prompt = lambda : "When do you want the job to run"
dialog.start.default = lambda : "now"
dialog.start.datatype = str
dialog.start.choices = lambda x : x in ('now', 'today', 'tomorrow') or time_check(x),
dialog.start.reformat = lambda x : time_check(x, True)

dialog.jobfile.prompt = lambda : "What will be the name of this new jobfile"
dialog.jobfile.default = lambda : f"{os.getenv('PWD')}/{dialog.jobname.answer}.slurm"
dialog.jobfile.datatype = str
dialog.jobfile.choices = lambda x : os.access(os.path.dirname(x), os.W_OK),
