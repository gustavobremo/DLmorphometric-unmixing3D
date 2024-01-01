"""
Created on Thur sept 22 2022

@author: Gustavo Bremo

Functions: 
Reads in an .czi file and generates datasets according to the parameter provided

"""

import argparse
import os
import random

import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageEnhance
from skimage import color, exposure, io
from stapl3d.preprocessing import shading


def brightness_augmentation(image, brightness_list):
    """
    Randomly adjusts the brightness of the input image based on a distribution of values.

    Args:
    - image (PIL.Image): The input image.
    - brightness_list (list): List of brightness values.

    Returns:
    - np.array: The augmented image with adjusted brightness.
    """
    # Convert the input image to a numpy array
    image = np.array(image)

    # Randomly select a brightness value from the provided list
    brightness = random.sample(brightness_list, 1)

    # Convert the numpy array back to a PIL image
    pil_output = Image.fromarray(image)

    # Create an enhancer to modify the brightness
    enhancer = ImageEnhance.Brightness(pil_output)

    # Apply the selected brightness enhancement
    output = enhancer.enhance(brightness[0])

    # Convert the output PIL image back to a numpy array
    augmented_image = np.array(output)

    return augmented_image


def get_patch(l, uby, ubx, patchsize, channels, channel_stacks, percentiles, mode, alpha, normalization, Brightness):
    """
    Extract a patch, normalize it based on percentile values for each channel, and create synthetic data.
    Concatenate AB images representing the source and target image.

    Args:
    - l:
    - uby:
    - ubx:
    - patchsize:
    - channels:
    - channel_stacks:
    - percentiles:
    - mode:
    - alpha:
    - normalization:
    - Brightness:

    Returns:
    - np.array: The concatenated AB image.
    """

    # Generate brightness range list for data augmentation
    brightness_range = [0.5, 3]
    brightnesslist = [round(x * 0.01, 2) for x in range(int(brightness_range[0] * 100), int(brightness_range[1] * 100), 1)]

    uby = int(uby)
    ubx = int(ubx)
    if alpha:
        alpha2 = round(1 - alpha, 2)

    # Random position within the image
    i_idx = random.randint(0, uby)
    j_idx = random.randint(0, ubx)
    yax = [i_idx, (i_idx + patchsize)]
    xax = [j_idx, (j_idx + patchsize)]
    rl = random.randint(0, l - 1)
    channel_normalized_patches_list = []

    # Extract patches and normalize them
    for c in range(channels):
        patch = channel_stacks[c][rl, yax[0] : yax[1], xax[0] : xax[1]]

        if normalization == "ac":
            normalized_patch = (patch / percentiles[c]) * 255
        if normalization == "od":
            normalized_patch = (patch / percentiles[2]) * 255

        normalized_patch[normalized_patch > 255] = 255
        channel_normalized_patches_list.append(normalized_patch)

    source_image = np.zeros((patchsize, patchsize, 3))

    # Modes to create training data
    if mode == "synthetic":
        synthetic_patch = (channel_normalized_patches_list[0] + channel_normalized_patches_list[1]) / 2
        synthetic_patch = synthetic_patch.astype(np.uint8)

        source_image[:, :, 0] = synthetic_patch.astype(np.uint8)
        source_image[:, :, 1] = synthetic_patch.astype(np.uint8)
        source_image[:, :, 2] = synthetic_patch.astype(np.uint8)

    elif mode == "weighted":
        synthetic_patch = cv2.addWeighted(channel_normalized_patches_list[0], alpha2, channel_normalized_patches_list[1], alpha, 0)
        synthetic_patch = synthetic_patch.astype(np.uint8)

        source_image[:, :, 0] = synthetic_patch.astype(np.uint8)
        source_image[:, :, 1] = synthetic_patch.astype(np.uint8)
        source_image[:, :, 2] = synthetic_patch.astype(np.uint8)

    elif mode == "real":
        source_image[:, :, 0] = channel_normalized_patches_list[2].astype(np.uint8)
        source_image[:, :, 1] = channel_normalized_patches_list[2].astype(np.uint8)
        source_image[:, :, 2] = channel_normalized_patches_list[2].astype(np.uint8)

    # Apply brightness augmentation if needed
    if Brightness:
        if random.randint(0, 100) < int(Brightness):
            source_image = brightness_augmentation(source_image.astype(np.uint8), brightnesslist)
        else:
            source_image = source_image.astype(np.uint8)

    target_image = np.zeros((patchsize, patchsize, 3))
    target_image[:, :, 0] = channel_normalized_patches_list[1].astype(np.uint8)
    target_image[:, :, 1] = channel_normalized_patches_list[0].astype(np.uint8)

    image_AB = np.concatenate([source_image, target_image], 1)

    return image_AB


def main_DataGenerator(
    filepath,
    percentile,
    patchsize,
    channels,
    l_layer,
    u_layer,
    biosample,
    datasize,
    mode,
    alpha,
    Norm,
    Brightness,
):
    """
    Automates patch extraction process and creates synthetic data.

    Args:
    - filepath: Path to the image file.
    - percentile: Percentile value for normalization.
    - patchsize: Size of the patch.
    - channels: Number of channels.
    - l_layer: Lower layer limit.
    - u_layer: Upper layer limit.
    - biosample: Biosample name.
    - datasize: Size of the dataset.
    - mode: Mode for data generation.
    - alpha: Alpha value (optional).
    - Norm: Normalization method.
    - Brightness: Brightness augmentation value.

    Returns:
    - None
    """
    # Converting input arguments to appropriate data types
    l_layer = int(l_layer)
    u_layer = int(u_layer)
    percentile = float(percentile)
    patchsize = int(patchsize)
    datasize = int(datasize)
    channels = int(channels)  # Number of channels

    if alpha:
        alpha = float(alpha)

    channel_stacks = []  # Collects all planes from all 3 channels
    percentiles = []  # List containing the calculated percentile value from each channel

    # LOADING THE CHANNEL DATA FROM THE 3D STACK AND CALCULATING PERCENTILE FOR EACH CHANNEL
    for i in range(channels):
        tmp_channel_stacked_planes = []  # Temporary list holding the collected stacked planes from channel "i"
        for j in range(l_layer, u_layer):
            data = shading.read_tiled_plane(filepath, i, j)  # Extracting layer (or plane) using the reading function
            dstacked = np.stack(data, axis=0)  # Stacking the tiles on top of each other
            tmp_channel_stacked_planes.append(dstacked)

        planes_stacked = np.vstack(tmp_channel_stacked_planes)  # Stacking all collected planes from a single channel
        channel_stacks.append(planes_stacked)  # Append stacked planes of a single channel to list
        flat_stacked_planes = planes_stacked.flatten()  # Making a 1D vector for percentile calculation
        p_val = np.percentile(planes_stacked, percentile)  # Calculating percentile value for the channel
        percentiles.append(p_val)  # Append percentile values to list

    # AUTOMATING PATCH EXTRACTION
    dimensions = channel_stacks[0].shape  # Get dimensions that will be used to extract patches
    l, y, x = dimensions  # Extract dimensions (l=layers, y and x tile size)

    ubx = x - patchsize  # Upperbound for x (avoid taking patch beyond frame size)
    uby = y - patchsize  # Upperbound for y

    # Defining proportions of the dataset
    t_train = int(datasize)
    t_test = int(t_train * 0.2)
    t_val = int(t_train * 0.2)

    # Creating folder names based on configurations
    if alpha:
        wb = str(alpha) + "_" + str(round(1 - alpha, 2))
        datafoldername = biosample + "_" + str(datasize) + "_" + Norm + "_" + mode + "_" + wb + "_patches"
    elif Brightness:
        datafoldername = biosample + "_" + str(datasize) + "_" + Norm + "_" + mode + "_br" + Brightness + "%" + "_patches"
    else:
        datafoldername = biosample + "_" + str(datasize) + "_" + Norm + "_" + mode + "_patches"

    # Creating necessary directories if they don't exist
    os.mkdir(datafoldername)
    if not os.path.exists(datafoldername + "/train"):
        os.mkdir(datafoldername + "/train")
    if not os.path.exists(datafoldername + "/test"):
        os.mkdir(datafoldername + "/test")
    if not os.path.exists(datafoldername + "/val"):
        os.mkdir(datafoldername + "/val")

    # Extracting patches for training, testing, and validation
    for t in range(t_train):
        image_AB = get_patch(
            l,
            uby,
            ubx,
            patchsize,
            channels,
            channel_stacks,
            percentiles,
            mode,
            alpha,
            Norm,
            Brightness,
        )
        matplotlib.image.imsave(datafoldername + "/train/" + str(t) + ".png", image_AB.astype(np.uint8))

    for t in range(t_test):
        image_AB = get_patch(
            l,
            uby,
            ubx,
            patchsize,
            channels,
            channel_stacks,
            percentiles,
            mode,
            alpha,
            Norm,
            Brightness,
        )
        matplotlib.image.imsave(datafoldername + "/test/" + str(t) + ".png", image_AB.astype(np.uint8))

    for t in range(t_val):
        image_AB = get_patch(
            l,
            uby,
            ubx,
            patchsize,
            channels,
            channel_stacks,
            percentiles,
            mode,
            alpha,
            Norm,
            Brightness,
        )
        matplotlib.image.imsave(datafoldername + "/val/" + str(t) + ".png", image_AB.astype(np.uint8))


def main():
    """
    Automates the generation of training data by extracting patches from a 3D stack.

    Command-line arguments:
    - --Filepath: Path to the .czi file.
    - --Percentile: Percentile value used for normalization (e.g., 95).
    - --PatchSize: Size of the patch as a single integer (e.g., 512).
    - --Channels: Number of channels from the 3D stack.
    - --BottomLayer: Bottom layer number.
    - --TopLayer: Top layer number.
    - --Biosample: Biological sample name.
    - --DatasetSize: Size of the training data to generate.
    - --DataMode: Type of data: synthetic | real | weighted. For weighted blending, alpha must be set.
    - --Alpha: Ch1 alpha value for blending. Ch2 alpha is automatically calculated as 1-alpha.
    - --Normalization: Normalization option for percentile value. Options: od = Open detector percentile, ac = All channels percentiles.
    - --Brightness: Percentage of brightness-augmented images in the dataset (enter as an integer, e.g., 50 for 50%).

    Returns:
    - None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--Filepath", help="Enter file path for .czi file")
    parser.add_argument("--Percentile", help="Enter percentile to normalize e.g 95")
    parser.add_argument("--PatchSize", help="Enter size of patch as single integer e.g 512")
    parser.add_argument("--Channels", help="Enter number of channels from 3D stack")
    parser.add_argument("--BottomLayer", help="Enter bottom layer number")
    parser.add_argument("--TopLayer", help="Enter top layer number")
    parser.add_argument("--Biosample", help="Enter biological sample name")
    parser.add_argument("--DatasetSize", help="Enter size of training data to generate")
    parser.add_argument(
        "--DataMode",
        help="Enter data type: synthetic | real | weighted. For weighted blending, alpha must be set",
    )
    parser.add_argument(
        "--Alpha",
        help="Enter ch1 alpha value for blending. Ch2 alpha is automatically calculated 1-alpha",
    )
    parser.add_argument(
        "--Normalization",
        help="Enter normalization option for percentile value. Options: od = Open detector percentile, ac = All channels percentiles",
    )
    parser.add_argument(
        "--Brightness",
        help="Enter percentage of brightness-augmented images in the dataset (enter as an integer, e.g., 50 -> means 50%)",
    )

    args = parser.parse_args()

    main_DataGenerator(
        args.Filepath,
        args.Percentile,
        args.PatchSize,
        args.Channels,
        args.BottomLayer,
        args.TopLayer,
        args.Biosample,
        args.DatasetSize,
        args.DataMode,
        args.Alpha,
        args.Normalization,
        args.Brightness,
    )
