## Converting separate band images into stacked RGB images #####

### Purpose

In order to facilitate the interpretation of images from Landsat images, a script was created
to process 13 single band images, into a stacked 3 channel representation of the images.

### Usage Steps

1) Run the get_images.sh script, with the parameters described bellow:

This script allows the user to load batches of Landsat images from Google Storage in an automated fashion, to get a view of the time series data.

```
./get_images.sh -h
[-h] -- program to retrieve landsat images from Google Storage  
 where: -h  show this help text 
 1st Argument: full path to gsutil instalation directory (ex: /home/gsutil_folder )  
 2nd Argument: image repository path (ex: gs://gcp-public-data-landsat ) 
 3rd Argument: image path (ex:164) 
 4th Argument: image row (ex: 058) 
 5th Argument: Landsat version (ex: 8) 
 6th Argument: time window (ex: 2017-2019) 
 7th Argument: output dir (full path) 

```


2) You can now execute the plot_3band_images_and_calculate_NDVI_NDWI.py script, with the following parameters:

	-home directory: The directory where you have unzipped your original file

	-stacked_image_destination: During the execution of the script, a file with this name will be generated

	-type of image generated: Currently, this script can generate three types of images.
	
		1 - Natural Color
	
		2 - Color Infrared (vegetation)

		3 - Vegetation Analysis

		4 - NDVI image
		
		5 - False Color Urban 

		6 - Agriculture

		7 - Atmospheric Penetration

		8 - Healthy Vegitation

		9 - Land Water

		10 - Atmospheric Removal

		11 - Short wave infrared

		all - All (DONT USE IF YOUR MACHINE DOESN'T HAVE A LOT OF MEMORY!! )
	-Label to tell if you want to process multiple images at once:
		yes
		no

Example execution:

Single image processing:  

```
python load_image.py "/home/manuel.mourato/shared_directory/
image_one/" "stacked_file_test.tif" 3 no
```
Batch image processing:

```
python load_image.py "/home/manuel.mourato/shared_directory/
image_one/" "stacked_file_test.tif" 3 yes 
```

3) If you go back to the directory where you have the original images, a new generated image should be there as well.
