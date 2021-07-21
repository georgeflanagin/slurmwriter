slurmscript = lambda info : f"""#!/bin/bash

###
# Note: slurm cannot see environment or shell variables. You
# must type in the values you need. You can add them in the 
# `sbatch` line you type in so that they are explicitly provided.
###

#SBATCH --account={info.account.answer}
#SBATCH --mail-type=ALL
#SBATCH --mail-user={info.username.answer}@richmond.edu
#SBATCH --mem={info.mem.answer}GB
#SBATCH --nodes=1
#SBATCH --ntasks-per-node={info.cores.answer}
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

"""

# """
# #!/bin/csh
# 
# #SBATCH --job-name=SiPOS_S1
# #SBATCH --output=SiPOS_S1.txt
# #SBATCH --partition=gpu
# #SBATCH --gres=gpu:rtx2080ti:1
# #SBATCH --ntasks=1
# #SBATCH --time=00:00:00
# 
# Print the simulation start date/time
# date
# 
# Print the GPU node the simulation is running on
# echo "I ran on:"
# cd $SLURM_SUBMIT_DIR
# echo $SLURM_NODELIST
# 
# Load the necessary program libraries
# module load amber/20
# 
# Set the output file directory
# cd /work/ja9ia/Si_POSS/PM6/MethoxyIndene/S1
# 
# Run Amber Jobs
# ./min.sh
# ./heat.sh
# ./eq.sh
# ./md.sh
# 
# Print the simulation end date/time
# date
# """
