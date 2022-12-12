# DLmorphometric-unmixing3D
Deep learning based approach for morphometric un-mixing of ex vivo multiplex 3D imaging data


<img src='imgs/img1.png' align="center" width=512>
<p align="justify">
The use of multiple fluorophores at the same time for the visualization of cellular structures can result in spectral overlap that makes it difficult to capture each signal independently. This project introduces a deep learning-based approach that employs a conditional generative adversarial network (cGAN) for un-mixing signals of cellular markers emitting the same fluorescent spectra into separate signals according to their sub-cellular distribution. As an alternative to conventional linear unmixing methods, this novel approach demonstrates its capability of separating signals when trained on both synthetic and real data derived from a 3D image of breast cancer organoids.

The repository contains the following:

- Code to generate training and testing data from beast cancer organoids 3D image dataset in CZI format

- Examples of generated data with various augmentation steps

- Deep learning training and testing examples 

- Code for calculating metrics and examples
</p>

## Datasets

### Preparing your own datasets for pix2pix
<p align="justify">
Paired images are the required input format for pix2pix training and testing. A Python script is provided here to generate training & testing data in the form of pairs of images [A,B] by extracting patches from the 3D dataset. **A** represents the source image with mixed signal, and **B** represents the target image with the un-mixed signal.</p>

<img src='imgs/img2.png' align="center" width=512>


GenerateData.sh is the bash script where all the parameters can be entered for running DataGenerator.py. The parameters contain the following options: 

- <p align="justify">File path for the 3D dataset. This patch extraction tool was designed only for the CZI file format with 3 channels, where the first and second are two different cellular markers, e.g., ch1 = CDH1 (membrane), ch2 = KI67 (nuclear), and ch3 = mixed signal (open detector)</p> 
- <p align="justify">Percentile value which can be a float and will be used to normalize the data acoording to the parameter option set in --Normalization</p>
- <p align="justify">Selection of patch size. This cannot exceed the size of the tile in the CZI file</p>
- <p align="justify">Number of channels must be set to 3 (further updates could remove this option)</p> 
- <p align="justify">Selection of the bottom and top layer to specify the range in the z-axis from which to extract patches</p>
- <p align="justify">"Biosample" allows you to enter a name for the dataset folder according to the organism from which the 3D image was acquired</p>
- <p align="justify">Selecting dataset sizes for the training and testing. When setting the --DataSize parameter, e.g., 1000, the code will generate 1000 training images and 10%, in this case 100 images will be generated for the testing</p>
- <p align="justify">Creating real, synthetic, or weighted blended data using "DataMode". When using the weighted blending option, the --Alpha parameter must be defined. The given alpha value is applied to ch1, and a (1-alpha) is automatically calculated for ch2</p>
- <p align="justify">Two different normalization approaches can be set. The first is to normalize each channel using its corresponding calculated percentile value. The second is to normalize all three channels using the calculated percentile value of the third channel</p>
- <p align="justify">Brightness augmentation can be implemented by entering an integer representing the percentage of data that will contain brightness variation. The brightness range is fixed and can be adjusted in the code</p>

After running the script will create a folder with subdirectories training, testing, and validation. 


## Trainings

<p align="justify">
The pix2pix framework was cloned from the repository [train_options.py](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/options/train_options.py) [Pix2Pix](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix.git). The framework can be implemented on a Linux or mac OS with Python 3 and
CPU or NVIDIA GPU + CUDA CuDNN.</p>
<p align="justify">
In order to train a model, the pix2pix has different parameter options which can be adjusted for the training. The first set of parameters are listed in the [base_options.py](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/options/base_options.py) and the second set in [train_options.py](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/options/train_options.py).To load the generated data created with the **DataGenerator.py**, a path of the dataset of this folder containing the training, testing set must be provided for the --dataroot parameter of the pix2pix. 
</p>

## Metrics






