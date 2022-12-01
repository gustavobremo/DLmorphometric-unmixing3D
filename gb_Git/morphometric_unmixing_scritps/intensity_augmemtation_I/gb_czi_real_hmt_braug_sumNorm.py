
import cv2
import numpy as np
from stapl3d.preprocessing import shading
import matplotlib.pyplot as plt
import argparse
from matplotlib import pyplot as plt
import matplotlib
import random
import time
import os
from PIL import Image, ImageEnhance

from skimage import io
from skimage import color
from skimage import exposure

filepath = "/hpc/pmc_rios/gbremo/projects/master_thesis/data/VMP_RL1_Exp001_VirtualMultiplexingGT/VMP_RL1_Exp001_Img010_mix4GT.czi"
per = 99
patchsize = 512
channels = 3
# l_layer = 0
# u_layer = 137
# l_layer = 0
# u_layer = 68
l_layer = 100
u_layer = 101
tiles = 49
datasize = 10
# biosample = "bc_org_real_hmt_braug_50p_sumNorm"
biosample = "test"
brightnessRange = [1,3]




#Function increases/decreases randomly the brightness of the passed imaged based on a distribution of values passed as a list
def BrightnessAugmentation(image,brightnesslist):
    image = np.array(image,dtype = 'uint8')
    brightness = random.sample(brightnesslist, 1)
    print(brightness)
    # print(brightness)
    pilOutput = Image.fromarray(image)
    enhancer = ImageEnhance.Brightness(pilOutput)
    output = enhancer.enhance(brightness[0])

    augmented_image = np.asarray(output)


    # return(output)
    return(augmented_image)


#FUNCTION RETURN PATCH AS AB IMAGE
# def get_patch(l,uby,ubx,patchsize,cr,ch_list,ch_percentile,p):
def get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,t,brightnesslist):
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
        percentile_value = percentiles[0]+percentiles[1]
        for c in range(channels):
            patch = channel_stacks[c][rl, yax[0]:yax[1],xax[0]:xax[1]]
            print("Channel: ",c)
            print("Tile layer: ",rl)
            print("ij position: ",yax[0],xax[0])
            
            # plt.imshow(patch)
            # plt.show()
            normalized_patch = (patch/percentile_value)*255         
            normalized_patch[normalized_patch> 255] = 255
            # plt.imshow(normalized_patch)
            # plt.show()
            channel_normalized_patches_list.append(normalized_patch)
        
        #     #CREATING PNGS

        # #Real image
        # real_image = np.zeros((patchsize, patchsize,3))
        # real_image[:,:,0] = channel_normalized_patches_list[2].astype(np.uint8)
        # real_image[:,:,1] = channel_normalized_patches_list[2].astype(np.uint8)
        # real_image[:,:,2] = channel_normalized_patches_list[2].astype(np.uint8)



        #-------------------------------------------------------------  
        # REAL DATASET    
        #Empty 3 channel RGB array for source image
        source_image = np.zeros((patchsize, patchsize,3),dtype = 'uint8')
        source_image[:,:,0] = channel_normalized_patches_list[2].astype(np.uint8)
        source_image[:,:,1] = channel_normalized_patches_list[2].astype(np.uint8)
        source_image[:,:,2] = channel_normalized_patches_list[2].astype(np.uint8)
        #-------------------------------------------------------------
        #Enhanding brightness of source image 
        # if random.randint(0,100) < 50:
        #     print("augmented")
        #     source_image = BrightnessAugmentation(source_image.astype(np.uint8),brightnesslist)
        # else:
        #     print("Not augmented")
        
        
        
        # plt.imshow(source_bright_image)
        # plt.show()
        # print(source_bright_image.shape)
        
        

        #Empty 3 channel RGB array for target image
        target_image = np.zeros((patchsize, patchsize,3),dtype = 'uint8')

        #Initializing array with normalized channel 1 and 2 values (Nuclear and Membrane different fluorophore)
        target_image[:,:,0] = channel_normalized_patches_list[1].astype(np.uint8)
        target_image[:,:,1] = channel_normalized_patches_list[0].astype(np.uint8)


        #HISTOGRAM MATCHING
        #----------------------------------------------------------
        matched_histograms = exposure.match_histograms(source_image,target_image, multichannel=True)
        matched = Image.fromarray(matched_histograms)
        
        gray_img = matched.convert('L') 
        gray_array = np.expand_dims(gray_img, axis=-1)


        # print(gray_img.shape)
        # print(gray_img.dtype)

        temp_image = np.zeros((512, 512,3),dtype = 'uint8')
        temp_image[:,:,0] = gray_array[:,:,0]
        temp_image[:,:,1] = gray_array[:,:,0]
        temp_image[:,:,2] = gray_array[:,:,0]

        source_bright_image = BrightnessAugmentation(temp_image,brightnesslist)

        # x = Image.fromarray(temp_image)
        # print("\n")
        # print(source_bright_image.shape)
        # print(source_bright_image.dtype)

        # print(gray_array.shape)
        # print(gray_array.dtype)

        # print(x.shape)
        # print(x.dtype)
        plt.imshow(source_bright_image)
        plt.show()

        # print(temp_image.shape)
        # plt.imshow(temp_image.astype(np.uint8))
        # plt.show()  

        # source_aug_image = temp_image.astype(np.uint8)

        # plt.imshow(temp_image.astype(np.uint8))
        # plt.show()
        #----------------------------------------------------------

        #-------------------------------------------------------------
        # #SYNTHETIC DATA OUGHT TO BE CREATED
        # synthetic_patch = (channel_normalized_patches_list[0]+channel_normalized_patches_list[1])/2
        # synthetic_patch = synthetic_patch.astype(np.uint8)
            
        # #SYNTHETIC DATASET Initializing array with normalized channel 3 values (Nuclear and Membrane same fluorophore)
        # source_image[:,:,0] = synthetic_patch
        # source_image[:,:,1] = synthetic_patch
        # source_image[:,:,2] = synthetic_patch
        #-------------------------------------------------------------




        end = time.time()
        T = end - start
        print("Total seconds: ",T)
        print("\n")

        # #Saving source and target png image
        image_AB = np.concatenate([temp_image,target_image], 1)
        # image_AB = np.concatenate([synthetic_image,target_image], 1)
        # image_AB = np.concatenate([source_image,synthetic_image,real_image,target_image], 1)

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
def main_DataGenerator(filepath,per,patchsize,channels,l_layer,u_layer,tiles,biosample,datasize,brightnessRange):
    #Generate brightness range list for data augmentation
    l = int(brightnessRange[0] * 100)
    u = int(brightnessRange[1]*100)
    brightnesslist = [round(x*0.01,2) for x in range(l,u,1)]

    print(brightnesslist)


    #parameters and datastructures for data acquisition
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
    #TESTING IMAGES
    # ch0 = channel_stacks[0]
    # ch1 = channel_stacks[1]
    # ch2 = channel_stacks[2]
    # fname0 = "channel_"+str(0)
    # fname1 = "channel_"+str(1)
    # fname2 = "channel_"+str(2)
    # # print(ch.shape)
    # os.mkdir(fname0)
    # os.mkdir(fname1)
    # os.mkdir(fname2)
    # for tile_idx in range(l):
    #     print(tile_idx)
    #     print(type(ch0[tile_idx,:,:]))
        # matplotlib.image.imsave(fname0+"/"+"File_"+str(tile_idx)+'.png', ch0[tile_idx,:,:].astype(np.uint8))
        # matplotlib.image.imsave(fname1+"/"+"File_"+str(tile_idx)+'.png', ch1[tile_idx,:,:].astype(np.uint8))
        # matplotlib.image.imsave(fname2+"/"+"File_"+str(tile_idx)+'.png', ch2[tile_idx,:,:].astype(np.uint8))
    #----------********----------
    datafoldername = biosample+"_"+"patches_data_"+str(int((datasize/1000)))+"k"
    os.mkdir(datafoldername)
    if os.path.exists(datafoldername+"/train")==False:
        os.mkdir(datafoldername+"/train")
    if os.path.exists(datafoldername+"/test")==False:
        os.mkdir(datafoldername+"/test")
    if os.path.exists(datafoldername+"/val")==False:
        os.mkdir(datafoldername+"/val")    



    #Extracting patches for training testing and validation
    print("Training set ************")
    for t in range(t_train):    
        print("Patch: ",t,"generating") 
        image_AB = get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,t,brightnesslist)
        # matplotlib.image.imsave(datafoldername+"/train/"+str(t)+'.png', image_AB.astype(np.uint8))
        io.imsave(datafoldername+"/train/"+str(t)+'.png', image_AB.astype(np.uint8))
    print("Testing set ************")
    for t in range(t_test):  
        image_AB = get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,t,brightnesslist)
        # matplotlib.image.imsave(datafoldername+"/test/"+str(t)+'.png', image_AB.astype(np.uint8))
        io.imsave(datafoldername+"/test/"+str(t)+'.png', image_AB.astype(np.uint8))
    print("Validating set ************")
    for t in range(t_val):  
        image_AB = get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,t,brightnesslist)
        # matplotlib.image.imsave(datafoldername+"/val/"+str(t)+'.png', image_AB.astype(np.uint8))
        io.imsave(datafoldername+"/val/"+str(t)+'.png', image_AB.astype(np.uint8))



main_DataGenerator(filepath,per,patchsize,channels,l_layer,u_layer,tiles,biosample,datasize,brightnessRange)




# if __name__ == '__main__':
#     #Commandline arguments
#     parser = argparse.ArgumentParser()
#     parser.add_argument("Filepath", help = "Enter file path for .ims file")
#     parser.add_argument("Percentile", help = "Enter percentile e.g 95")
#     parser.add_argument("PatchSize", help = "Enter size of patch as single integer e.g 512")
#     parser.add_argument("DatasetSize", help = "Enter the total number of patches to generate")
#     args = parser.parse_args()

#     main_DataGenerator(args.Filepath,args.Percentile,args.PatchSize,args.DatasetSize)

