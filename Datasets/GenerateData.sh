#When using for whole stack, run as sbatch with high mem= ...GB


source "/hpc/pmc_rios/.stapl3d.ini" && load_stapl3d_config
source /hpc/local/CentOS7/pmc_rios/anaconda3/etc/profile.d/conda.sh
conda activate stapl3d-dev1.0.0



#Real
python DataGenerator.py --Filepath /hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi --Percentile 99 --PatchSize 512 --Channels 3 --BottomLayer 67 --TopLayer 69 --Biosample bc_organoid --DatasetSize 10 --DataMode real --Normalization ac 
python DataGenerator.py --Filepath /hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi --Percentile 99 --PatchSize 512 --Channels 3 --BottomLayer 67 --TopLayer 69 --Biosample bc_organoid --DatasetSize 10 --DataMode real --Normalization od

#Synthetic
python DataGenerator.py --Filepath /hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi --Percentile 99 --PatchSize 512 --Channels 3 --BottomLayer 67 --TopLayer 69 --Biosample bc_organoid --DatasetSize 10 --DataMode synthetic --Normalization ac
python DataGenerator.py --Filepath /hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi --Percentile 99 --PatchSize 512 --Channels 3 --BottomLayer 67 --TopLayer 69 --Biosample bc_organoid --DatasetSize 10 --DataMode synthetic --Normalization od

#Weighted
python DataGenerator.py --Filepath /hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi --Percentile 99 --PatchSize 512 --Channels 3 --BottomLayer 67 --TopLayer 69 --Biosample bc_organoid --DatasetSize 10 --DataMode weighted --Alpha 0.2 --Normalization ac
python DataGenerator.py --Filepath /hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi --Percentile 99 --PatchSize 512 --Channels 3 --BottomLayer 67 --TopLayer 69 --Biosample bc_organoid --DatasetSize 10 --DataMode weighted --Alpha 0.4 --Normalization ac
python DataGenerator.py --Filepath /hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi --Percentile 99 --PatchSize 512 --Channels 3 --BottomLayer 67 --TopLayer 69 --Biosample bc_organoid --DatasetSize 10 --DataMode weighted --Alpha 0.6 --Normalization ac
python DataGenerator.py --Filepath /hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi --Percentile 99 --PatchSize 512 --Channels 3 --BottomLayer 67 --TopLayer 69 --Biosample bc_organoid --DatasetSize 10 --DataMode weighted --Alpha 0.8 --Normalization ac

#Brightness augmentation
python DataGenerator.py --Filepath /hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi --Percentile 99 --PatchSize 512 --Channels 3 --BottomLayer 67 --TopLayer 69 --Biosample bc_organoid --DatasetSize 10 --DataMode real --Normalization od --Brightness 50
python DataGenerator.py --Filepath /hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi --Percentile 99 --PatchSize 512 --Channels 3 --BottomLayer 67 --TopLayer 69 --Biosample bc_organoid --DatasetSize 10 --DataMode synthetic --Normalization od --Brightness 50



