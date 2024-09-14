#!/bin/bash

#SBATCH --job-name=model_test_suite
#SBATCH -o model_test_suite.out
#SBATCH -e model_test_suite.err
#SBATCH --time=24:00:00
#SBATCH -N 1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=2
#SBATCH --mem=80G
#SBATCH -p gpu
#SBATCH --gres=gpu:1
#SBATCH --mail-user= email_id 
#SBATCH --mail-type=ALL

# Load required modules
module load Python/3.9.6-GCCcore-11.2.0
module load CUDA/11.3.1
# Set scratch directory variable (recommended to use PFSDIR for larger files)
SCRATCH_DIR=/scratch/users/(username)
SLURM_SUBMIT_DIR=(working directory)

# Create the scratch directory if it does not exist
mkdir -p $SCRATCH_DIR

# Copy necessary files to the scratch directory
scp -r pioneer.case.edu:$SLURM_SUBMIT_DIR/* $SCRATCH_DIR

# Change to the scratch directory
cd $SCRATCH_DIR

# Run your Python script
python model_test_suite.py 2

# Copy results back to the submission directory
scp -r * pioneer.case.edu:$SLURM_SUBMIT_DIR

# Clean up scratch space if not needed anymore
rm -rf $SCRATCH_DIR/*

