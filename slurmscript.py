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
# Note: slurm cannot see environment or shell variables. You
# must type in the values you need. You can add them in the 
# `sbatch` line you type in so that they are explicitly provided.
###

#SBATCH --account={info.account.answer}
#SBATCH --begin={info.start.answer}
#SBATCH --mail-type=ALL
#SBATCH --mail-user={info.username.answer}@richmond.edu
#SBATCH --mem={info.mem.answer}GB
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={info.cores.answer}
#SBATCH --partition={info.partition.answer}
#SBATCH --time={info.time.answer}

#SBATCH -o {info.output.answer}
#SBATCH -e {info.output.answer}.err

cd $SLURM_SUBMIT_DIR
echo "I ran on: $SLURM_NODELIST"
echo "Starting at `date`"

###
# Environment setup
###

NAME={info.jobname.answer}

DATADIR={info.datadir.answer}

SCRATCH={info.scratchdir.answer}

########################################################################
# Always a good idea to wipe anything from memory where it
# is allocated. Add other modules here, as well.
########################################################################

module purge

mkdir -p $SCRATCH

########################################################################
# Copy data from DATADIR to SCRATCH below.
########################################################################


########################################################################
# Run your job by adding commands below.
########################################################################


########################################################################
# Copy output files from SCRATCH to ... local storage? ... below.
########################################################################

 
########################################################################
# Be kind and clean the SCRATCH area.
########################################################################

rm -rf $SCRATCH

echo "Finished at `date`"

"""
