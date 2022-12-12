import os
from random import randrange
from readline import remove_history_item
from skimage.io import imread
from skimage.metrics import structural_similarity as ssimsk
import cv2
from skimage.transform import resize
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import statistics
import pandas as pd

import image_similarity_measures
from image_similarity_measures.quality_metrics import rmse, psnr, ssim


#This is a list containing the name of the experiments.
experiment_prefix = ["real_newnorm_nobr","real_newnorm_br"]



def saveimage(ri,fi,s,i,m):

    fig, axes = plt.subplots(1,2,sharex=True)


    # plt.imshow(rB)
    axes[0].imshow(ri)
    axes[0].set_title("True")    
    axes[1].imshow(fi)
    axes[1].set_title("Generated")
    fig.tight_layout()
  
    fig.suptitle(("SSIM: "+m+" "+str(s)), fontsize=16)
    
    plt.savefig("ssim/"+m+"_"+str(i)+"_"+".png",dpi=300)
    
    plt.close()
    
    

def getSSIM(r,f,i):
    #reading the images of the real and fake
    rB = imread(r)
    fB = imread(f)

    #image to dislay
    #Grabbing the nuclear image of the real 
    realpax8img = rB.copy()
    realpax8img[:,:,1] = 0
    realpax8img[:,:,2] = 0
    #Grabbing the nuclear image of the fake
    fakepax8img = fB.copy()
    fakepax8img[:,:,1] = 0
    fakepax8img[:,:,2] = 0
    
    #Grabbing the membrane image of the real 
    realCDH1img = rB.copy()
    realCDH1img[:,:,0] = 0
    realCDH1img[:,:,2] = 0
    #Grabbing the membrane image of the fake
    fakeCDH1img = fB.copy()
    fakeCDH1img[:,:,0] = 0
    fakeCDH1img[:,:,2] = 0


    #Skimage
    s_pax8 = ssimsk(realpax8img,fakepax8img,multichannel=True,gaussian_weights=True, sigma=1.5, use_sample_covariance=False, win_size=11, data_range = 255)
    s_CDH1 = ssimsk(realCDH1img,fakeCDH1img,multichannel=True,gaussian_weights=True, sigma=1.5, use_sample_covariance=False, win_size=11, data_range = 255)    


    return(s_pax8,s_CDH1)

#------------------------------------------------------------------------------------------------------------------------------------------------

def getPSNR(r,f,i):
    # rB = imread(folder+"/"+r.split("/")[-1])
    # fB = imread(folder+"/"+f.split("/")[-1])    
    rB = imread(r)
    fB = imread(f)

    #image to dislay
    #PAX8
    realpax8img = rB.copy()
    realpax8img[:,:,1] = 0
    realpax8img[:,:,2] = 0

    fakepax8img = fB.copy()
    fakepax8img[:,:,1] = 0
    fakepax8img[:,:,2] = 0
    
    #CDH1
    realCDH1img = rB.copy()
    realCDH1img[:,:,0] = 0
    realCDH1img[:,:,2] = 0

    fakeCDH1img = fB.copy()
    fakeCDH1img[:,:,0] = 0
    fakeCDH1img[:,:,2] = 0

    #channel to calculate SSIM from real image
    rB_pax8 = rB[:,:,0]
    fB_pax8 = fB[:,:,0]

    rB_CDH1 = rB[:,:,1]
    fB_CDH1 = fB[:,:,1]

    #Skimage
    # s_pax8 = ssimsk(realpax8img,fakepax8img,multichannel=True,gaussian_weights=True, sigma=1.5, use_sample_covariance=False, win_size=11, data_range = 255)
    # s_CDH1 = ssimsk(realCDH1img,fakeCDH1img,multichannel=True,gaussian_weights=True, sigma=1.5, use_sample_covariance=False, win_size=11, data_range = 255)    

    # s_pax8 = ssimsk(rB_pax8,fB_pax8,multichannel=True,gaussian_weights=True, sigma=1.5, use_sample_covariance=False, win_size=11, data_range = 255)
    # s_CDH1 = ssimsk(rB_CDH1,fB_CDH1,multichannel=True,gaussian_weights=True, sigma=1.5, use_sample_covariance=False, win_size=11, data_range = 255)  

    #image_similarity_measures SSIM
    # s_pax8 = ssim(rB_pax8,fB_pax8)
    # s_CDH1 = ssim(rB_CDH1,fB_CDH1)

    # image_similarity_measures PSNR
    s_pax8 = cv2.PSNR(rB_pax8, fB_pax8)
    s_CDH1 = cv2.PSNR(rB_CDH1,fB_CDH1)

    # saveimage(realpax8img,fakepax8img,s_pax8,i,"pax8")
    # saveimage(realCDH1img,fakeCDH1img,s_CDH1,i,"CDH1")

    return(s_pax8,s_CDH1)
#------------------------------------------------------------------------------------------------------------------------------------------------

#Create df categories
def get_categories(category,n):
    
    categories = []
    #repeating n labels of the same category
    for k in range(n):
        categories.append(category)
    
    df_cat = pd.DataFrame(categories)
    # df_cat = df_cat.transpose()
    df_cat.columns = ["experiment"]
    # print(df_cat)
    return(df_cat)


#------------------------------------------------------------------------------------------------------------------------------------------------
#Function creating a dataframe containing all the measured SIIM for each channel for each experiment
def create_dataframe(prefix,mode):
    #keeps order of the pix2pix generated output folder that was used to analyze. 
    order_experiments = []


    #Getting main directories containing generated output. 
    #In the pix2pix framework there is a folder "results" containing generated results. 
    # These generated results are stored as follows:
    # "model experiment name" folder
        # test_latest
            # images
                # here are all generated images of the pix2pix

    # main folder refers to the root folder "model experiment name" 
    # Many of these folder can be put in a single directory to analyize various experiments
    main_folders = filter(os.path.isdir, os.listdir(os.getcwd()))
    #Sorting these folders
    sorted_main_folders = sorted(main_folders)
    # list containing al ssim score df the nucearl and membrane channel respectively of each experiment. 
    main_nuclei_df_list = []
    main_membrane_df_list = []

    j = 0

    mode_status = ""
    #Going through each experiment folder
    for folder in sorted_main_folders:
        print(folder)
        order_experiments.append(folder)
        #path to generated images file directory
        directory = os.path.join(folder,"test_latest","images")

        #Obtaining the files from the image folder containing all true A, true B, fake B images
        files = os.listdir(directory)
        files = sorted(files)
        #gettin all ssim for nuclear and membrane channel for a single experiment
        nuclear_ssim = []
        membrane_ssim = []


        #Get SSIM between the real and fake images both for 2 channels
        #Getting all filenames for the real and fake images
        realList = [r for r in files if "real_B.png" in r]
        fakeList = [f for f in files if "fake_B.png" in f]
        #For all images in the real and fake list
        for i in range(len(realList)):
            #get the path for the real and corresonding generated "fake" image
            f = os.path.join(directory,fakeList[i])
            r = os.path.join(directory,realList[i])

            print(f)
            print(r)
            print("\n")
            #Options to calculate ssim or psnr. Can be set when calling the function. 
            if mode == "ssim":
                #calls function to calculate ssim for the nulear and membrane. 
                nuclear, membrane = getSSIM(r,f,i)
                mode_status = "SSIM"
            elif mode == "psnr":
                nuclear, membrane = getPSNR(r,f,i)
                mode_status = "PSNR"
            # appending calculated ssim for each channel
            nuclear_ssim.append(nuclear)
            membrane_ssim.append(membrane)
            print(i)
        #Creating categorical lables for the channels
        x = ["KI67","CDH1"]

        y = [nuclear_ssim,membrane_ssim]

        print(x)
        print(y)
        #Get categorical labels for the experiments
        exp_cat_df_nucl = get_categories(x[0],len(realList))
        exp_cat_df_mem = get_categories(x[1],len(realList))
        nucl_cat_df = get_categories(prefix[j],len(realList))
        memb_cat_df = get_categories(prefix[j],len(realList))

        #creating a pandas dataframe nuclear with categories
        df_nuclear = pd.DataFrame(y[0])
        # df_nuclear = df_nuclear.transpose()
        df_nuclear = pd.concat([exp_cat_df_nucl,nucl_cat_df, df_nuclear], axis=1)
        df_nuclear.columns = ["Channels","Training",mode_status]

        #collecting df data for nuclei to concatenate later
        main_nuclei_df_list.append(df_nuclear)
        
        #creating a pandas dataframe membrane with categories
        df_membrane = pd.DataFrame(y[1])
        # df_nuclear = df_nuclear.transpose()
        df_membrane = pd.concat([exp_cat_df_mem,memb_cat_df, df_membrane], axis=1)
        df_membrane.columns = ["Channels","Training",mode_status]

        #collecting df data for nuclei to concatenate later
        main_membrane_df_list.append(df_membrane)


        df = pd.concat([df_nuclear, df_membrane], axis=0)
        
        print("\n")
        print(df)


        j = j+1

    joined_df_list = main_nuclei_df_list + main_membrane_df_list
    mainframe = 0
    for k in range(len(joined_df_list)):
        
        if k == 0:
            mainframe = joined_df_list[0]
        else:
            mainframe = pd.concat([mainframe, joined_df_list[k]], axis=0)



    print(mainframe)
    mainframe.to_csv(mode_status+'_distributions_data_categorized.csv', index=False)

    with open('exp_order.txt', 'a') as exp_file:
        for f in order_experiments:
            exp_file.write(f"{f}\n")

create_dataframe(experiment_prefix,"ssim")
