#!/usr/bin/env bash
#SBATCH --job-name=generate_Data1k
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=RTX6000:1
#SBATCH --mem=100G
#SBATCH --time=05:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --output=10k_output.txt
#SBATCH --error=10k_error.txt

source "/hpc/pmc_rios/.stapl3d.ini" && load_stapl3d_config
source /hpc/local/CentOS7/pmc_rios/anaconda3/etc/profile.d/conda.sh
conda activate stapl3d-dev1.0.0

python gb_r_br_80_05_3_odN_99_10k.py
