
from logging import raiseExceptions
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

filepath = "/hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi"
per = 99
patchsize = 512
channels = 3
l_layer = 100
u_layer = 101
tiles = 49
datasize = 1
biosample = "bc_organoid"

#FUNCTION RETURN PATCH AS AB IMAGE
# def get_patch(l,uby,ubx,patchsize,cr,ch_list,ch_percentile,p):
def get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,t):
        print("Processing patch")   
        #GETTING COORDINATES FOR PATCH EXTRACTION
        #get random ij position of the image
        # i_idx = random.randint(0,uby)<----------------------
        # j_idx = random.randint(0,ubx)<----------------------
        i_idx = 56
        j_idx = 47
        #Turning it into slice indices
        yax = [i_idx, (i_idx+patchsize)]
        xax = [j_idx, (j_idx+patchsize)]

        #Get random layer value (considering all layers)
        # rl = random.randint(0,l-1)<----------------------
        rl = 13

        #Checking running time
        start = time.time()

        #EXTRACTING PATCHES
        #List containing all channel patches
        channel_normalized_patches_list = []
        #For  each channel, get a patch

        for c in range(channels):
            patch = channel_stacks[c][rl, yax[0]:yax[1],xax[0]:xax[1]]
            print("Channel: ",c)
            print("Tile layer: ",rl)
            print("ij position: ",yax[0],xax[0])
            
            # plt.imshow(patch)
            # plt.show()
            normalized_patch = (patch/percentiles[c])*255         
            normalized_patch[normalized_patch> 255] = 255
            # plt.imshow(normalized_patch)
            # plt.show()
            channel_normalized_patches_list.append(normalized_patch)
        
        #     #CREATING PNGS
        #Empty 3 channel RGB array for source image
        source_image = np.zeros((patchsize, patchsize,3))
            
        # #SYNTHETIC DATA OUGHT TO BE CREATED
        # synthetic_patch = (channel_normalized_patches_list[0]+channel_normalized_patches_list[1])/2
        # synthetic_patch = synthetic_patch.astype(np.uint8)
            
        #Initializing soure image array with normalized channel 3 values (Nuclear and Membrane open detector)
        source_image[:,:,0] = channel_normalized_patches_list[2].astype(np.uint8)
        source_image[:,:,1] = channel_normalized_patches_list[2].astype(np.uint8)
        source_image[:,:,2] = channel_normalized_patches_list[2].astype(np.uint8)


        # plt.imshow(source_image)
        # plt.show()
        #Empty 3 channel RGB array for target image
        target_image = np.zeros((patchsize, patchsize,3))

        #Initializing array with normalized channel 1 and 2 values (Nuclear and Membrane different fluorophore)
        target_image[:,:,0] = channel_normalized_patches_list[1].astype(np.uint8)
        target_image[:,:,1] = channel_normalized_patches_list[0].astype(np.uint8)

        # plt.imshow(target_image)
        # plt.show()

        end = time.time()
        T = end - start
        print("Total seconds: ",T)
        print("\n")

        # #Saving source and target png image
        image_AB = np.concatenate([source_image, target_image], 1)

        # plt.imshow(image_AB)
        # plt.show()

        return(image_AB)
        # return(0)
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
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
            #Add stacked plane to temp list collecting each plane
            tmp_channel_stacked_planes.append(dstacked)
        print("Compiling list for channel: ",i)
        #Stacking all planes as the following dimensions l,y,x   
        planes_stacked = np.vstack(tmp_channel_stacked_planes)
        #Append stacked planes of a single channel to list
        channel_stacks.append(planes_stacked)
        #Making a 1D vector for percentile calculation
        flat_stacked_planes = planes_stacked.flatten()
        #Calculating percentile
        p_val = np.percentile(planes_stacked, per)
        p_val2 = np.percentile(flat_stacked_planes, per)

        #Append percentile values to list
        percentiles.append(p_val)
    
    #PREPARING FOR PATCH EXTRACTION
    #Get dimensions that will be used to extract patches
    dimensions = channel_stacks[0].shape

    # print(channel_stacks[0].shape)
 

    # print(dimensions)
    print("\n")
    print("Percentiles ch1,ch2,ch3 :",percentiles)
    print("\n")
    #Getting single dimension values 
    l = dimensions[0]
    y = dimensions[1]
    x = dimensions[2]
    print("\n")
    print(l,y,x)
    #Upperbound for x and y (avoid taking patch beyond frame size)
    ubx = x-patchsize
    uby = y-patchsize
    print(ubx)
    print(uby)
    #Defining proportions of the dataset
    t_train = int(datasize)
    t_test  = int(t_train*0.2)
    t_val   = int(t_train*0.2)
    print("\n")

    #----------********----------

    #----------********----------
    datafoldername = biosample+"_"+"patches_data_"+str(int((datasize/1000)))+"k"
    os.mkdir(datafoldername)
    if os.path.exists(datafoldername+"/train")==False:
        os.mkdir(datafoldername+"/train")
    # if os.path.exists(datafoldername+"/test")==False:
    #     os.mkdir(datafoldername+"/test")
    # if os.path.exists(datafoldername+"/val")==False:
    #     os.mkdir(datafoldername+"/val")    



    #Extracting patches for training testing and validation
    print("Training set ************")
    for t in range(t_train):    
        print("Patch: ",t,"generating") 
        image_AB = get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,t)
        matplotlib.image.imsave(datafoldername+"/train/"+str(t)+'.png', image_AB.astype(np.uint8))
    # print("Testing set ************")
    # for t in range(t_test):  
    #     image_AB = get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,t)
    #     matplotlib.image.imsave(datafoldername+"/test/"+str(t)+'.png', image_AB.astype(np.uint8))
    # print("Validating set ************")
    # for t in range(t_val):  
    #     image_AB = get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,t)
    #     matplotlib.image.imsave(datafoldername+"/val/"+str(t)+'.png', image_AB.astype(np.uint8))



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

