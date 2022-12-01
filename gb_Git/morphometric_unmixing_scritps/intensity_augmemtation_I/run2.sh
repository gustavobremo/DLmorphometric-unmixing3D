#!/usr/bin/env bash
#SBATCH --job-name=generate_Data1k
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=RTX6000:1
#SBATCH --mem=100G
#SBATCH --time=00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --output=wblnd_output.txt
#SBATCH --error=wblnd_error.txt

source "/hpc/pmc_rios/.stapl3d.ini" && load_stapl3d_config
source /hpc/local/CentOS7/pmc_rios/anaconda3/etc/profile.d/conda.sh
conda activate stapl3d-dev1.0.0

#python gb_czi_real_braug_sumNorm.py
#python gb_czi_synth_braug_sumNorm.py
#python gb_czi_real_braug_sumNorm_p25.py
#python gb_czi_synth_braug_sumNorm_75.py
python gb_czi_synth_braug_sumNorm_25.py
