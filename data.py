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
import sys

import argparse
import getpass
import math
import platform
import pprint
import random
import resource
import time

###
# Parts of this project.
###

from   sloppytree import SloppyTree
from   gkfdecorators import trap

###
# The netid of the user running this instance of the program.
###

me = lambda : getpass.getuser()
mynetid = getpass.getuser()

# partitions represent where you want to run the program
partitions = SloppyTree()

community_partitions_compute = ('basic', 'medium', 'large')
community_partitions_plenum = ('basic', 'medium', 'large', 'ML', 'sci')
condos = ('bukach', 'diaz', 'erickson', 'johnson', 'parish', 'yang1', 'yang2', 'yangnolin')

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
programs.amber20.modules = ('amber/20')
programs.amber20.artition_choices = tuple(( _ for _ in partitions.keys()))
###
# Each of the trees is a decision tree for the user.
###

dialog = SloppyTree()

dialog.username.answer = mynetid

dialog.jobname.prompt = lambda : "Name of your job"

dialog.output.prompt = lambda : "Name of your job's output file"
dialog.output.default = lambda : f"{dialog.jobname.answer}.txt"

dialog.partition.prompt = lambda : "Name of the partition where you want to run your job"
dialog.partition.default = lambda : 'basic'

dialog.account.prompt = lambda : f"What account is your user id, {mynetid}, associated with"
dialog.account.default = lambda : f"ur-community"

dialog.datadir.prompt = lambda : "Where is your input data directory"
dialog.datadir.default = lambda : f"{os.getenv('HOME')}"

dialog.scratchdir.prompt = lambda : "Where is your scratch directory"
dialog.scratchdir.default = lambda : f"/scratch/{mynetid}"

dialog.mem.prompt = lambda : "How much memory (in GB)"
dialog.mem.default = lambda : 16
dialog.cores.prompt = lambda : "How many cores"
dialog.cores.default = lambda : 8
dialog.time.prompt = lambda : "How long should this run (in hours)"
dialog.time.default = lambda : 1

dialog.jobfile.prompt = lambda : "What will be the name of this new jobfile"
dialog.jobfile.default = lambda : f"{os.getenv('HOME')}/{dialog.jobname.answer}.slurm"


