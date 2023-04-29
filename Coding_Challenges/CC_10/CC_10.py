# Coding Challenge 10
# Our coding challenge this week that improves our practice with rasters from Week 10.
#
# Task 1 - Use what you have learned to process the Landsat files provided, this time, you know you are interested
# in the NVDI index which will use Bands 4 (red, aka vis) and 5 (near-infrared, aka nir) from the Landsat 8 imagery, see here for more info about the bands: https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites. Data provided are monthly (a couple are missing due to cloud coverage) during the year 2015 for the State of RI, and stored in the file Landsat_data_lfs.zip.
#
# Before you start, here is a suggested workflow:
#
# Extract the Landsat_data_lfs.zip file into a known location.
# For each month provided, you want to calculate the NVDI, using the equation: nvdi = (nir - vis) / (nir + vis)
# https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index. Consider using the Raster Calculator Tool in
# ArcMap and using "Copy as Python Snippet" for the first calculation.
# The only rule is, you should run your script once, and generate the NVDI for ALL MONTHS provided. As part of your
# code submission, you should also provide a visualization document (e.g. an ArcMap layout in PDF format), showing the
# patterns for an area of RI that you find interesting.


import arcpy
import os

#### CHANGE INPUT DIRECTORY ####
input_directory = r'C:\Users\OpenTron\Documents\NRS528\Coding Challenges\CC_10\DATA'

os.chdir(input_directory)
arcpy.env.workspace = os.curdir
arcpy.env.overwriteOutput = True

# List folders in directory
list_folders = os.listdir(os.curdir)
list_folders = [x for x in list_folders if os.path.isdir(x)]

print('Processing the following folders...', list_folders)


# Loop through each folder
for folder in list_folders:
    print('... Starting month ' + folder)
    os.chdir(folder)

    # List all rasters in folder and loop through it
    rasters_tif = arcpy.ListRasters("*", "TIF")
    raster_list = []
    raster_name_list = []
    for raster in rasters_tif:
        if raster.split('.')[0][-2:] in 'B4':
            raster_list.append(raster)
            raster_name_list.append('VIS')
        if raster.split('.')[0][-2:] in 'B5':
            raster_list.append(raster)
            raster_name_list.append('NIR')

    # Raster Calculator tool
    output_raster = arcpy.ia.RasterCalculator(raster_list, raster_name_list, "(NIR-VIS)/(NIR+VIS)")
    os.chdir('../')
    output_raster.save(folder + '_NDVI.tif')

print('All Done!')
