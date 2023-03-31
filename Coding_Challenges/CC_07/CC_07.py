# Coding Challenge 7
# Our coding challenge this week should make use of temporary folders, output folders and file management.
#
# Convert your Coding Challenge 5 exercise to work with temporary folders, os.path.join and glob.glob. Do not take too
# much time on this and if you do not have a working Challenge 5, talk to the instructor.

#### Solution Starts Here ####

# The following script creates heatmaps for the sightings of different species. The data includes two species,
# Emperor Goose and Pelagic Cormorant, two very common birds in North America. The data was downloaded from the USGS
# Alaskan Service Center, and so provides data of the bird's sighting in Alaska. Because Alaska is so large, the
# map frame spans the whole globe. Not sure if there is another projection system to use or which if I should have
# changed the extent to make it look better.
#
# Sources:
# Uher-Koch, B.D., Schmutz, J.A., Hupp, J.W., Ely, C.R., Douglas, D.C., 2021, Tracking data for Emperor geese
# (Anser canagicus) (ver 1.0, April 2021): U.S. Geological Survey data release, https://doi.org/10.5066/P9GJQ6LF
# Hatch, S.A., Gill, V.A., Mulcahy, D.M., Douglas, D.C., 2020, Tracking data for Pelagic cormorants (Phalacrocorax
# pelagicus) (ver 1.0, August 2020): U.S. Geological Survey data release, https://doi.org/10.5066/P9Y5PQY3


# import packages
import csv
import pandas as pd
import arcpy
import glob
import os

#### USER INPUTS ####
species_names = ['Emperor Goose', 'Pelagic Cormorant']  # Provide names of species in first column of csv
species_names_short = ['Goose', 'Cormorant']    # Provide shortened names for more concise file naming
#### USER INPUTS ####

print('Setting up workspace...')
# Use os and glob to get csv file
os.chdir("DATA")
file = glob.glob("*.csv")
file = file[0]

# Arcpy environment
arcpy.env.overwriteOutput = True
arcpy.env.workspace = os.curdir
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)

# Set up temporary and output directories
keep_temp_files = False  # Change to true if you want to keep temp files
if not os.path.exists("temporary_files"):
    os.mkdir("temporary_files")
if not os.path.exists("output_files"):
    os.mkdir("output_files")
temp = 'temporary_files'
output = 'output_files'

print('Starting csv processing...')
# Create lists and dataframes to track longitudes (x) and latitudes (y) and convert to individual csv file
species1_X = []
species1_Y = []
species1_df = pd.DataFrame()
species2_X = []
species2_Y = []
species2_df = pd.DataFrame()
#
# Open csv file to sort through each species
with open(file) as data:
    next(data)
    for row in csv.reader(data):
        if row[0] in species_names[0]:
            species1_X.append(row[3])
            species1_Y.append(row[2])
        else:
            species2_X.append(row[3])
            species2_Y.append(row[2])

# Convert lists into dataframe and make csv file using df.to_csv
species1_df['X'] = species1_X
species1_df['Y'] = species1_Y
species2_df['X'] = species2_X
species2_df['Y'] = species2_Y

species1_df.to_csv(os.path.join(temp,species_names_short[0] + '.csv'))
species2_df.to_csv(os.path.join(temp,species_names_short[1] + '.csv'))

print('Finished csv processing...')

# Process between each species dataset to create a heat map of sightings within a grid
print('Starting arcpy processing...')

# Edit Species List
os.chdir(temp)
csv_list = glob.glob('*.csv')

for item in csv_list:
    in_table = item
    item = item.split('.')[0]
    x_coord = 'X'
    y_coord = 'Y'
    z_coord = ""
    out_layer = item
    saved_Layer = item + '_points.shp'
    spRef = arcpy.SpatialReference(4326)  # 4326 == WGS 1984

    # Create shapefile
    lyr = arcpy.MakeXYEventLayer_management(in_table, x_coord, y_coord, out_layer, spRef, z_coord)
    arcpy.CopyFeatures_management(lyr, saved_Layer)

    # Calculate the extent
    desc = arcpy.Describe(lyr)
    Xmin = desc.extent.XMin
    Ymin = desc.extent.YMin
    Xmax = desc.extent.XMax
    Ymax = desc.extent.YMax

    # Create Fishnet using extent, change cell size if needed
    print('Creating Fishnet for ' + item + '...')
    outFeatureClass = item + '_Fishnet.shp'
    originCoordinate = str(Xmin) + ' ' + str(Ymin)  # Left bottom of our point data
    yAxisCoordinate = str(Xmin) + ' ' + str(Ymin + 1)  # +1 latitude to head north
    cellSizeWidth = "1"  # 1 x1 degrees grid
    cellSizeHeight = "1"
    numRows = ""  # Leave blank, as we have set cellSize
    numColumns = ""  # Leave blank, as we have set cellSize
    oppositeCorner = str(Xmax) + ' ' + str(Ymax)  # i.e. max x and max y coordinate
    labels = "NO_LABELS"
    templateExtent = "#"  # No need to use, as we have set yAxisCoordinate and oppositeCorner
    geometryType = "POLYGON"  # Create a polygon, could be POLYLINE

    arcpy.CreateFishnet_management(outFeatureClass, originCoordinate, yAxisCoordinate,
                                   cellSizeWidth, cellSizeHeight, numRows, numColumns,
                                   oppositeCorner, labels, templateExtent, geometryType)

    # Spatial Join between species shapefile and fishnet
    print('Started Spatial Join for ' + item + '...')
    target_features = item + '_Fishnet.shp'
    join_features = saved_Layer
    out_feature_class = item + "_HeatMap.shp"
    join_operation = "JOIN_ONE_TO_ONE"
    join_type = "KEEP_ALL"
    field_mapping = ""
    match_option = "INTERSECT"
    search_radius = ""
    distance_field_name = ""

    arcpy.SpatialJoin_analysis(target_features, join_features, out_feature_class,
                               join_operation, join_type, field_mapping, match_option,
                               search_radius, distance_field_name)

    print(item + ' heatmap created...')

os.chdir('../')
# Move file to Output folder and delete Temporary folder
arcpy.management.CopyFeatures(os.path.join(temp, item + '_HeatMap.shp'), os.path.join(output, item + '_HeatMap.shp'))

if keep_temp_files == False:
    arcpy.Delete_management('temporary_files')

print('All Done!')

