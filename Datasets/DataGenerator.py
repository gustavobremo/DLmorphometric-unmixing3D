"""
Created on Thur sept 22 2022

@author: Gustavo Bremo

Functions: 
Reads in an .czi file and generates datasets according to the parameter provided

"""

import numpy as np
from stapl3d.preprocessing import shading
import matplotlib.pyplot as plt
import argparse
from matplotlib import pyplot as plt
import matplotlib
import random
import os
import cv2
from PIL import Image, ImageEnhance
from skimage import io
from skimage import color
from skimage import exposure



#Function increases/decreases randomly the brightness of the passed imaged based on a distribution of values passed as a list
def BrightnessAugmentation(image,brightnesslist):
    image = np.array(image)
    brightness = random.sample(brightnesslist, 1)
    print(brightness)
    # print(brightness)
    pilOutput = Image.fromarray(image)
    enhancer = ImageEnhance.Brightness(pilOutput)
    output = enhancer.enhance(brightness[0])

    augmented_image = np.array(output)

    return(augmented_image)

#Function extracts patch, normalizes it based on percentile value of each channel, and creates syntheic data, returning concatenated AB images representing the source and target image.
def get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,mode,alpha,normalization,Brightness):
    
    #Generate brightness range list for data augmentation
    #Hard coded the range of brightness. a value of 1 the yields no change. Lower than 1, image gets darger. Higher than 1, image gets brighter.
    # Lower bound is 0.5 and upper bound is 3.
    brightnessRange = [0.5,3]
    #generating a list containing values between 0.5 and 3 with steps of 0.01 representing brightness degrees that will be sampled for introducing brightness. 
    l = int(brightnessRange[0] * 100)
    u = int(brightnessRange[1]*100)
    brightnesslist = [round(x*0.01,2) for x in range(l,u,1)]

    print("Processing patch")   
    #setting arguments to integers
    uby = int(uby)
    ubx = int(ubx)
    #alpha value for membrane channel
    if alpha:
        alpha2 = round(1-alpha,2)


    #----------****GETTING COORDINATES FOR PATCH EXTRACTION****----------
    #get random ij position point in the tile image. 
    #uby "upper bound y" and ubx "upper bound x" are limits of the y and x axis in the image in order to avoid slecting an area where a patch falls outside of the image range.
    i_idx = random.randint(0,uby)
    j_idx = random.randint(0,ubx)
    #Each list contains two indices selecting a range in the corresponding axis starting from the "i or j"th point up to the lenght of a patch size i.e 512
    yax = [i_idx, (i_idx+patchsize)]
    xax = [j_idx, (j_idx+patchsize)]

    #Generates a random number representing a random selection of a layer (all layers are considered here)
    rl = random.randint(0,l-1)

    
    #----------****EXTRACTING PATCHES****----------
    #List containing normalized patch from all three channels
    channel_normalized_patches_list = []

    #For each channel, get the patch using the indices in the yax and xax lists
    for c in range(channels):
        #extracting the patch from channel "c" from the layer "rl" of the stack 
        patch = channel_stacks[c][rl, yax[0]:yax[1],xax[0]:xax[1]]
        print("Channel: ",c)
        print("Tile layer: ",rl)
        print("ij position: ",yax[0],xax[0])
        
        if normalization == "ac":
            # Normalizing the patch using the percentile of the current channel "c"
            normalized_patch = (patch/percentiles[c])*255         

        if normalization == "od":
            # Normalizing the patch using the highest percentile (open detector channel percentile)
            normalized_patch = (patch/percentiles[2])*255     

        # Clipping the values, anything higher than 255 is set to 255
        normalized_patch[normalized_patch> 255] = 255
        #Adding the normalized patch of current channel "c" to the list which collects all 3 channels. 
        channel_normalized_patches_list.append(normalized_patch)
    
    
    #Empty 3 channel RGB array for source image
    source_image = np.zeros((patchsize, patchsize,3))
        
        
    if mode == "synthetic":
        #Creating the synthetic patch by taking the mean value of the nuclear and membrane channel 
        synthetic_patch = (channel_normalized_patches_list[0]+channel_normalized_patches_list[1])/2
        synthetic_patch = synthetic_patch.astype(np.uint8)

        #Introducing the Synthetic patch in each channel of the source image (RGB)
        source_image[:,:,0] = synthetic_patch.astype(np.uint8)
        source_image[:,:,1] = synthetic_patch.astype(np.uint8)
        source_image[:,:,2] = synthetic_patch.astype(np.uint8)

    elif mode == "weighted":
        #Creating the synthetic weighted blended patch by taking the mean value of the nuclear and membrane channel blended with alpha and 1-alpha
        synthetic_patch = cv2.addWeighted(channel_normalized_patches_list[0], alpha2, channel_normalized_patches_list[1],alpha, 0)
        synthetic_patch = synthetic_patch.astype(np.uint8)

        #Introducing the Synthetic patch in each channel of the source image (RGB)
        source_image[:,:,0] = synthetic_patch.astype(np.uint8)
        source_image[:,:,1] = synthetic_patch.astype(np.uint8)
        source_image[:,:,2] = synthetic_patch.astype(np.uint8)

    elif mode == "real":
        #Introducing the Real patch in each channel of the source image (RGB)
        source_image[:,:,0] = channel_normalized_patches_list[2].astype(np.uint8)
        source_image[:,:,1] = channel_normalized_patches_list[2].astype(np.uint8)
        source_image[:,:,2] = channel_normalized_patches_list[2].astype(np.uint8)

    if Brightness:
            #Enhancing brightness of source image 
        if random.randint(0,100) < int(Brightness):
            print("augmented")
            source_image = BrightnessAugmentation(source_image.astype(np.uint8),brightnesslist)
        else:
            print("Not augmented")
            source_image = source_image.astype(np.uint8)

    #----------****CREATING TARGET IMAGE****----------
    #Empty 3 channel RGB array for target image
    target_image = np.zeros((patchsize, patchsize,3))

    #Introducing the nuclear channel in the Red channel and membrane in the Green channel
    target_image[:,:,0] = channel_normalized_patches_list[1].astype(np.uint8)
    target_image[:,:,1] = channel_normalized_patches_list[0].astype(np.uint8)

    #Concatenating the source and the target image to get the AB format for pix2pix
    image_AB = np.concatenate([source_image, target_image], 1)

    #Return the concatenated AB image
    return(image_AB)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

#MAIN function automating the patch extraction process
def main_DataGenerator(filepath,percentile,patchsize,channels,l_layer,u_layer,biosample,datasize,mode,alpha,Norm,Brightness):
    l_layer = int(l_layer)
    u_layer = int(u_layer)
    percentile = float(percentile)
    patchsize = int(patchsize)
    datasize = int(datasize)
    #Number of channels from the stack as integers  | channels(1=Open detector, 2=nuclear, 3=membrane)
    channels = int(channels)
    if alpha:
        alpha = float(alpha)



    #Collects all planes from all 3 channels
    channel_stacks = []
    #List containing the calculated percentile value from each channel from the stack 
    percentiles = []
    
    #LOADING THE CHANNEL DATA FROM THE 3D STACK AND CALCULATING PERCENTILE FOR EACH CHANNEL
    #For each channel in the 3Dstack
    for i in range(channels):
        #Temporary list holding the collected stacked planes from channel "i" each iteration
        tmp_channel_stacked_planes = []
        print("Loading channel: ",i)
        #For each layer in the range of lower and uper layer limits
        for j in range(l_layer,u_layer):
            print("Adding layer: ",j)
            #Extracting layer (or plane) using the reading function from stapl3D. The plane consist of 49 tiles. 
            data = shading.read_tiled_plane(filepath,i,j)
            #Stacking the 49 tiles on top of each other. 
            dstacked = np.stack(data, axis=0)
            #Add stacked tiles from the single plane to temp list collecting each plane
            tmp_channel_stacked_planes.append(dstacked)
        print("Compiling list for channel: ",i)
        #Stacking all collected planes from a single channel as the following dimensions l,y,x   
        planes_stacked = np.vstack(tmp_channel_stacked_planes)
        #Append stacked planes of a single channel to list which collects all channel planes. 
        channel_stacks.append(planes_stacked)
        #Making a 1D vector for percentile calculation
        flat_stacked_planes = planes_stacked.flatten()
        #Calculating percentile value for the channel "i"
        p_val = np.percentile(planes_stacked, percentile)

        #Append percentile values to list
        percentiles.append(p_val)
    
    #AUTOMATING PATCH EXTRACTION
    #Get dimensions that will be used to extract patches
    dimensions = channel_stacks[0].shape 


    print("\n")
    print("Percentiles ch1,ch2,ch3 :",percentiles)
    print("\n")
    #Getting dimension of 3D stack l=layers, y and x tile size
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

 
    #----------****CREATING FOLDERS****----------
    if alpha:
        wb = str(alpha)+"_"+str(round(1-alpha,2))
        datafoldername = biosample+"_"+str(datasize)+"_"+Norm+"_"+mode+"_"+wb+"_patches"

    elif Brightness:
        datafoldername = biosample+"_"+str(datasize)+"_"+Norm+"_"+mode+"_br"+Brightness+"%"+"_patches"
    else:
        datafoldername = biosample+"_"+str(datasize)+"_"+Norm+"_"+mode+"_patches"


    os.mkdir(datafoldername)
    if os.path.exists(datafoldername+"/train")==False:
        os.mkdir(datafoldername+"/train")
    if os.path.exists(datafoldername+"/test")==False:
        os.mkdir(datafoldername+"/test")
    if os.path.exists(datafoldername+"/val")==False:
        os.mkdir(datafoldername+"/val")    


    #----------********----------
    #Extracting patches for training testing and validation
    print("Training set ************")
    #Generating training set
    for t in range(t_train):    
        print("Patch: ",t,"generating") 
        #Random patch is extracted and a synthetic source image and a ground truth target image is returned concatenated in AB png format
        image_AB = get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,mode,alpha,Norm,Brightness)
        #Saving the AB patch
        matplotlib.image.imsave(datafoldername+"/train/"+str(t)+'.png', image_AB.astype(np.uint8))
    print("Testing set ************")
    for t in range(t_test):  
        #Random patch is extracted and a synthetic source image and a ground truth target image is returned concatenated in AB png format
        image_AB = get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,mode,alpha,Norm,Brightness)
        #Saving the AB patch
        matplotlib.image.imsave(datafoldername+"/test/"+str(t)+'.png', image_AB.astype(np.uint8))
    print("Validating set ************")
    for t in range(t_val):  
        #Random patch is extracted and a synthetic source image and a ground truth target image is returned concatenated in AB png format
        image_AB = get_patch(l,uby,ubx,patchsize,channels,channel_stacks,percentiles,mode,alpha,Norm,Brightness)
        #Saving the AB patch
        matplotlib.image.imsave(datafoldername+"/val/"+str(t)+'.png', image_AB.astype(np.uint8))





if __name__ == '__main__':
    #Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--Filepath", help = "Enter file path for .czi file")
    parser.add_argument("--Percentile", help = "Enter percentile to normalize e.g 95")
    parser.add_argument("--PatchSize", help = "Enter size of patch as single integer e.g 512")
    parser.add_argument("--Channels", help = "Enter number of channels from 3D stack")
    parser.add_argument("--BottomLayer", help = "Enter bottom layer number")
    parser.add_argument("--TopLayer", help = "Enter top layer number")
    parser.add_argument("--Biosample", help = "Enter biological sample name")
    parser.add_argument("--DatasetSize", help = "Enter size of training data to generate")
    parser.add_argument("--DataMode", help = "Enter data type: synthethic | real | weighted | For weighted blending alpha must be set")
    parser.add_argument("--Alpha", help = "Enter ch1 alpha value for blending | ch2 alpha is automaticall calculated 1-alpha")
    parser.add_argument("--Normalization", help = "Enter normalization option for percentile value| od = Open detector percentile, ac = All channels percentiles")
    parser.add_argument("--Brightness", help = "Enter percentage of brighness augmented images in the dataset| enter as integer e.g. 50 -> means 50%")


    args = parser.parse_args()

                      
    main_DataGenerator(args.Filepath,args.Percentile,args.PatchSize,args.Channels,args.BottomLayer,args.TopLayer,args.Biosample,args.DatasetSize,args.DataMode,args.Alpha,args.Normalization,args.Brightness)



