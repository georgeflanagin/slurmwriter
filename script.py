"""
This file contains the template for the scripts for the SLURM 
job processor. The template is a lambda function so that 
evaluation is delayed until runtime.
"""

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

slurmscript = lambda info : f"""#!/bin/bash

###
# This file was originally created by SLURMwriter, a tool
# written by University of Richmond's High Performance
# Computing group. This file created @ {info.written.foo()}
# 
# Note: slurm cannot see environment or shell variables. You
# must type in the values you need. You can add them in the 
# `sbatch` line you type in so that they are explicitly provided.
###

###
# Environment setup
###
export JOBID=$SLURM_JOB_ID
export NETID={info.username.answer}
export JOBNAME={info.jobname.answer}
export DATADIR="$HOME/{info.jobname.answer}"
export SCRATCH="/localscratch/$NETID/$JOBNAME/$JOBID"
export BIGSCRATCH="/scratch/$NETID/$JOBNAME/$JOBID"

echo DATADIR=$DATADIR
echo SCRATCH=$SCRATCH
echo BIGSCRATCH=$BIGSCRATCH

mkdir -p $DATADIR
mkdir -p $SCRATCH
mkdir -p $BIGSCRATCH

###
# Invoke function as a trap on the EXIT signal to ensure
# the node's scratch directory is clean.
###
clean_scratch()
{{
    cause=$?
    if [[ cause != 0 ]]; then
        echo "Killed by signal $cause" >> "$HOME/$JOBNAME.$JOBID.err"
    else
        echo "Normal termination." >> "$HOME/$JOBNAME.$JOBID.err"
    fi
    nice cp -r $SCRATCH/* $BIGSCRATCH/.
    rm -fr $SCRATCH
}}

#SBATCH --account={info.account.answer}
#SBATCH --begin={info.start.answer}
#SBATCH --mail-type=ALL
#SBATCH --mail-user="$NETID@richmond.edu"
#SBATCH --mem={info.mem.answer}GB
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={info.cores.answer}
#SBATCH --partition={info.partition.answer}
#SBATCH --time={info.time.answer}

#SBATCH -o "$HOME/$JOBNAME.$JOBID.out"
#SBATCH -e "$HOME/$JOBNAME.$JOBID.err"

cd $SLURM_SUBMIT_DIR
echo "I ran on: $SLURM_NODELIST"
echo "Starting at `date`"

########################################################################
# Add other modules here, as well.
########################################################################

export MODULEPATH="$MODULEPATH:/usr/local/sw/modulefiles"
{info.modules}

########################################################################
# Copy data from DATADIR to SCRATCH below.
########################################################################
cp -r $DATADIR/* $SCRATCH/.


########################################################################
# Run your job by adding commands below for {info.program.answer}. 
########################################################################
cd "$SCRATCH"

trap clean_scratch EXIT
{info.joblines}
trap "" EXIT

echo "Finished at `date`"
"""
