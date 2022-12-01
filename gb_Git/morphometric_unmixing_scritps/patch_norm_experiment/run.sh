#!/usr/bin/env bash
#SBATCH --job-name=patchescreate
#SBATCH --partition=cpu

#SBATCH --mem=80G
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --output=hd_5k_output.txt
#SBATCH --error=hd_5k_error.txt

source "/hpc/pmc_rios/.stapl3d.ini" && load_stapl3d_config
source /hpc/local/CentOS7/pmc_rios/anaconda3/etc/profile.d/conda.sh
conda activate stapl3d-dev1.0.0

python synthetic_patch_generator_alpha_blending_single_dataset.py
