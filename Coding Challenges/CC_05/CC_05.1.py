# Coding Challenge 5
# For this coding challenge, I want you to practice the heatmap generation that we went through in class,
# but this time obtain your own input data, and I want you to generate heatmaps for TWO species.
#
# You can obtain species data from a vast array of different sources, for example:
#
# obis - Note: You should delete many columns (keep species name, lat/lon) as OBIS adds some really long strings
# that don't fit the Shapefile specification.
# GBIF
# Maybe something on RI GIS
# Or just Google species distribution data
# My requirements are:
#
# The two input species data must be in a SINGLE CSV file, you must process the input data to separate out the
# species (Hint: You can a slightly edited version of our CSV code from a previous session to do this), I recommend
# downloading the species data from the same source so the columns match.
# Only a single line of code needs to be altered (workspace environment) to ensure code runs on my computer, and
# you provide the species data along with your Python code.
# The heatmaps are set to the right size and extent for your species input data, i.e. appropriate fishnet cellSize.
# You leave no trace of execution, except the resulting heatmap files.
# You provide print statements that explain what the code is doing, e.g. Fishnet file generated.

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

####### CHANGE PATH WHERE combined_species_clean.csv is located #######
path = 'DATA/combined_species_clean.csv'

# Create lists and dataframes to track longitudes (x) and latitudes (y) and convert to individual csv file
goose_x = []
goose_y = []
goose_df = pd.DataFrame()
cormorant_x = []
cormorant_y = []
cormorant_df = pd.DataFrame()

# Open csv file to sort through each species
with open(path) as data:
    next(data)
    for row in csv.reader(data):
        if row[0] in 'Emperor Goose':
            goose_x.append(row[3])
            goose_y.append(row[2])
        else:
            cormorant_x.append(row[3])
            cormorant_y.append(row[2])

# Convert lists into dataframe and make csv file using df.to_csv
goose_df['x'] = goose_x
goose_df['y'] = goose_y
cormorant_df['x'] = cormorant_x
cormorant_df['y'] = cormorant_y

goose_df.to_csv('DATA/Goose_solo.csv')
print('Goose CSV created')
cormorant_df.to_csv('DATA/Cormorant_solo.csv')
print('Cormorant CSV created')

# Initiate arcpy environment
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'C:\Users\OpenTron\Documents\NRS528\Coding Challenges\CC_05\DATA'
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)

# Process between each species dataset to create a heat map of sightings within a grid

# Edit Species List, making sure the file names are called 'SPECIESNAME'_solo.csv
speciesList = ['Cormorant', 'Goose']
for item in speciesList:
    print('Started ' + item + ' processing')
    in_Table = item +'_solo.csv'
    x_coord = 'x'
    y_coord = 'y'
    z_coord = ""
    out_layer = item
    saved_Layer = item + '.shp'
    spRef = arcpy.SpatialReference(4326)  # 4326 == WGS 1984

    # Create shapefile
    lyr = arcpy.MakeXYEventLayer_management(in_Table, x_coord, y_coord, out_layer, spRef, z_coord)
    arcpy.CopyFeatures_management(lyr, saved_Layer)

    # Calculate the extent
    desc = arcpy.Describe(lyr)
    Xmin = desc.extent.XMin
    Ymin = desc.extent.YMin
    Xmax = desc.extent.XMax
    Ymax = desc.extent.YMax

    # Create Fishnet using extent, change cell size if needed
    print('Creating Fishnet')
    outFeatureClass = item + "_fishnet.shp"
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
    print('Started Spatial Join')
    target_features = item + "_fishnet.shp"
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

    print(item + ' heatmap created')

    if arcpy.Exists(saved_Layer):
        arcpy.Delete_management(saved_Layer)
        print(item + ' shape file deleted')
    if arcpy.Exists(item + "_fishnet.shp"):
        arcpy.Delete_management(item + "_fishnet.shp")
        print(item + ' fishnet deleted')

print('All done')