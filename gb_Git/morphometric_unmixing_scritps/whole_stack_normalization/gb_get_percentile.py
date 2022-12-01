
from logging import raiseExceptions
from statistics import median_high
from xml.dom import registerDOMImplementation
import numpy as np
from stapl3d.preprocessing import shading
import matplotlib.pyplot as plt
import argparse
from matplotlib import pyplot as plt
import matplotlib
import random
import time
import os
import cv2
import gc

filepath = "/hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi"
per = 99
patchsize = 512
channels = 3
l_layer =0
u_layer = 137
# l_layer =100
# u_layer = 104
tiles = 49
datasize = 10
biosample = "bc_organoid_full_stacks_normalization_all_layers"



#FUNCTION RETURN PATCH AS AB IMAGE
# def get_patch(l,uby,ubx,patchsize,cr,ch_list,ch_percentile,p):
def get_patch(l,uby,ubx,patchsize,channels,channel_stacks,p_val,t):
        print("Processing patch")   
        #GETTING COORDINATES FOR PATCH EXTRACTION
        #get random ij position of the image
        i_idx = random.randint(0,uby)
        j_idx = random.randint(0,ubx)
        #Turning it into slice indices
        yax = [i_idx, (i_idx+patchsize)]
        xax = [j_idx, (j_idx+patchsize)]

        #Get random layer value (considering all layers)
        rl = random.randint(0,l-1)

        #Checking running time
        start = time.time()

        #EXTRACTING PATCHES
        #List containing all channel patches
        channel_normalized_patches_list = []
        #For  each channel, get a patch

        #Randomly select alpha values
        
        percentile_value = p_val
        for c in range(channels):
            patch = channel_stacks[c][rl, yax[0]:yax[1],xax[0]:xax[1]]
            print("Channel: ",c)
            print("Tile layer: ",rl)
            print("ij position: ",yax[0],xax[0])


            normalized_patch = (patch.astype(np.float64)/percentile_value)*255         
            # normalized_patch = (patch.astype(np.float64)/percentiles[2])*255         
            # normalized_patch = (patch.astype(np.float64)/percentiles[c])*255         
            normalized_patch[normalized_patch> 255] = 255
            channel_normalized_patches_list.append(normalized_patch)
        
        
        #     #CREATING PNGS
        #Empty 3 channel RGB array for source image
        source_image = np.zeros((patchsize, patchsize,3))
            
        # #SYNTHETIC DATA OUGHT TO BE CREATED
        # synthetic_patch = (channel_normalized_patches_list[0]+channel_normalized_patches_list[1])/2 <------------------------------------------------------------
        # synthetic_patch = cv2.addWeighted(channel_normalized_patches_list[0], alpha1, channel_normalized_patches_list[1],alpha2, 0)
        
        #Generate source image array with normalized channel 3 values (Nuclear and Membrane open detector)
        
        source_image[:,:,0] = channel_normalized_patches_list[2].astype(np.uint8)
        source_image[:,:,1] = channel_normalized_patches_list[2].astype(np.uint8)
        source_image[:,:,2] = channel_normalized_patches_list[2].astype(np.uint8)


        #Empty 3 channel RGB array for target image
        target_image = np.zeros((patchsize, patchsize,3))

        #Initializing array with normalized channel 1 and 2 values (Nuclear and Membrane different fluorophore)
        target_image[:,:,0] = channel_normalized_patches_list[1].astype(np.uint8)
        target_image[:,:,1] = channel_normalized_patches_list[0].astype(np.uint8)


        end = time.time()
        T = end - start
        print("Total seconds: ",T)
        print("\n")

        # #Saving source and target png image
        image_AB = np.concatenate([source_image, target_image], 1)


        return(image_AB)
        # return(0)

# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
def main_DataGenerator(filepath,per,patchsize,channels,l_layer,u_layer,tiles,biosample,datasize):
    channels = int(channels)
    channel_stacks = []
    percentiles = []
    #Loading data
    for i in range(channels):
        tmp_channel_stacked_planes = []
        print("Loading channel: ",i)
        for j in range(l_layer,u_layer):
            print("Adding layer: ",j)
            data = shading.read_tiled_plane(filepath,i,j)
            # matplotlib.image.imsave(str(i)+"_"+str(j)+'.png',data.astype(np.uint8))#*****************************************************
            dstacked = np.stack(data, axis=0)
            dstacked = dstacked.flatten()
            print("dstacked flatten:",dstacked.shape)
            #Add stacked plane to temp list collecting each plane
            # tmp_channel_stacked_planes.append(dstacked)
            tmp_channel_stacked_planes = np.concatenate([tmp_channel_stacked_planes, dstacked], 0)
            # tmp_channel_stacked_planes.append(dstacked)
        print("Compiling stacks for channel: ",i)
        #Stacking all planes as the following dimensions l,y,x   
        print("TMP channel list with flatten tiles: ",tmp_channel_stacked_planes.shape)
        # planes_stacked = np.stack(tmp_channel_stacked_planes,axis= 0)
        
        #Append stacked planes of a single channel to list
        # channel_stacks.append(planes_stacked)
        channel_stacks = np.concatenate([channel_stacks,tmp_channel_stacked_planes], 0)

    # all_channels = np.concatenate((channel_stacks[0],channel_stacks[1],channel_stacks[2]))
    print(channel_stacks.shape)
    #Making a 1D vector for percentile calculation
    # channel_stacks = np.vstack(channel_stacks)
    # channel_stacks = channel_stacks.flatten()
    
    # flat_stacked_planes_multiple = channel_stacks[:].flatten()
    print("\n")

    # print("Flat dimension multiple stacks ",flat_stacked_planes_multiple.shape)
    # print("Flat all channels dimension: ",flat_stacked_planes.shape)

    #Calculating percentile
    p_val = np.percentile(channel_stacks, per)

    # p_val = np.percentile(planes_stacked, per)
    # p_val2 = np.percentile(flat_stacked_planes, per)

    # print("Percval not flat: ",p_val)
    print("Percval flat: ",p_val)
    with open("percentile.txt", "w") as text_file:
        text_file.write("Percentile is: %s" % p_val)

#CHECK THE IMGSAVE DPI


main_DataGenerator(filepath,per,patchsize,channels,l_layer,u_layer,tiles,biosample,datasize)



# if __name__ == '__main__':
#     #Commandline arguments
#     parser = argparse.ArgumentParser()
#     parser.add_argument("Filepath", help = "Enter file path for .ims file")
#     parser.add_argument("Percentile", help = "Enter percentile e.g 95")
#     parser.add_argument("PatchSize", help = "Enter size of patch as single integer e.g 512")
#     parser.add_argument("DatasetSize", help = "Enter the total number of patches to generate")
#     args = parser.parse_args()

#     main_DataGenerator(args.Filepath,args.Percentile,args.PatchSize,args.DatasetSize)


