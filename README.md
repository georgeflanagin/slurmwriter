# slurmwriter
Tool to assist users with writing SLURM jobs

## Usage
`python slurmwriter.py`

You will then be asked a series of contextual questions, based on your login (`netid`).
The program will take your information and create a correctly formatted SLURM jobfile.

`slurmwriter` pays attention. The program may be run interactively or driven from a 
script. In the case of scripted input, there are several additional features:

1. `slurmwriter` will ignore everything after the sharp (#), allowing you 
to write lines in your file like this `100   # GB of memory` so that 
you can document your script that builds SLURM jobs.
1. `slurmwriter` can build several jobs, rather than just one. You can 
concatenate several requests, and put `EOF` on the last line, and `slurmwriter`
will stop there.

## Caveats

`slurmwriter` queries the computer where it is running to get information
about the installed programs, and it does this at the time it is launched.
The information is correct and up-to-date, but it is possible that your 
user may not be able to see every partition or run every program.


## Program maintenance

All the information used by `slurmwriter` is in the file `rules.py`. 
