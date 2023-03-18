########################
# The following script builds on my Coding Challenge 4 assignment, in which metrics that summarize the area around a
# road are calculated. The results of this work will assist a research project to develop an enhanced street sweeping
# program, which will optimize the location and frequency of street sweeping. The following metrics are calculated as
# percentage of area within a buffer zone around each road segment:

#     1. Percent Land Usage - Residential, Commercial, and Forested
#     2. Percent Impervious Surface Area
#     3. Percent Canopy Coverage (plus average tree height)
#     4. Percent Building Coverage

# These metrics are all significant in terms of pollutant accumulation, and therefore are important factors
# for deciding the prioritization of street sweeping. Some additional factors that will be included in future work
# are road slope, road quality, presence of bike lanes, and watershed impairment.
#
# The data was downloaded from two different sources. (1) https://rigis-edc.opendata.arcgis.com/ was the source of
# the land use, impervious surfaces, and building locations. (2) https://glad.umd.edu/dataset/gedi was the source of
# the canopy coverage and tree height data. All the data was preprocessed slightly to ensure the files were not too
# large. They are all projected into the Rhode Island State Plane with units of feet.
#
# The output of this script will be located in your "*input_directory*/output_files" folder. Explore the dataset by
# adjusting the symbology for each metric to see how they vary around the study area. Some future work will be to
# determine equations to combine these metrics to make road priority models for each season.

# This will take anywhere from 1 to 3 minutes to run, depending on the size of the study area
########################

import time
# Track run time
start_time = time.time()

import arcpy
import os

###### USER INPUTS ######
input_directory = r"C:\Users\OpenTron\Documents\NRS528\Midterm\DATA"
study_area = ['WARWICK', 'EAST GREENWICH'] # Input desired municipalities in RI (all caps) - MAX 3!
###### USER INPUTS #####

# Set up arcpy environment
arcpy.env.overwriteOutput = True
arcpy.env.workspace = input_directory

# Set up temporary and output directories
keep_temp_files = False     # Change to true if you want to keep temp files
if not os.path.exists(os.path.join(input_directory, "temporary_files")):
    os.mkdir(os.path.join(input_directory, "temporary_files"))
if not os.path.exists(os.path.join(input_directory, "output_files")):
    os.mkdir(os.path.join(input_directory, "output_files"))
output = 'output_files'
temp = 'temporary_files'

#### Select study area. Change line 37 for desired study area
print('1. Selecting Study Area')

in_feature = r'Municipalities_RISPft.shp'
out_feature = os.path.join(temp, 'Study_Area.shp')
if len(study_area) == 1:
    where_clause = "NAME = '" + study_area[0] + "'"
elif len(study_area) == 2:
    where_clause = "NAME = '" + study_area[0] + "' OR NAME = '" + study_area[1] + "'"
elif len(study_area) == 3:
    where_clause = "NAME = '" + study_area[0] + "' OR NAME = '" + study_area[1] + "' OR NAME = '" + study_area[2] + "'"
arcpy.analysis.Select(in_feature, out_feature, where_clause)

# Set extent base on study area
desc = arcpy.Describe(out_feature)
arcpy.env.extent = arcpy.Extent(desc.extent.XMin, desc.extent.YMin, desc.extent.XMax, desc.extent.YMax)

#### Road and Buffer setup
print('2. Setting Up Roads and Buffer Zones')

# Select state roads
in_feature = r'Roads_RISPft.shp'
out_feature = 'in_memory/State_Roads'
where_clause = "JURIS = 2 Or JURIS = 3"     # State maintained roads have jurisdiction of 2 or 3
arcpy.analysis.Select(in_feature, out_feature, where_clause)

# Clip to municipality borders
in_feature = 'in_memory/State_Roads'
clip_feature = os.path.join(temp, 'Study_Area.shp')
out_feature = 'in_memory/Roads_Clipped'
arcpy.analysis.Clip(in_feature, clip_feature, out_feature)

# Dissolve and format roads to have 0.1 mile segments
in_feature = 'in_memory/Roads_Clipped'
out_feature = 'in_memory/Roads_Dissolved'
arcpy.management.Dissolve(in_feature, out_feature)

# Generate points along line that are 0.1 miles apart
in_feature = 'in_memory/Roads_Dissolved'
out_feature = 'in_memory/Roads_Points'
distance = '0.1 miles'
arcpy.management.GeneratePointsAlongLines(in_feature, out_feature, 'DISTANCE', distance, Include_End_Points='END_POINTS')

# Split line at points - this will create your final roads dataset
in_feature = 'in_memory/Roads_Dissolved'
point_feature = 'in_memory/Roads_Points'
out_feature = os.path.join(temp,'Final_Roads.shp')
search_radius = '50 feet'
arcpy.management.SplitLineAtPoint(in_feature, point_feature, out_feature, search_radius)

# Create buffer zone around roads
in_feature = out_feature
out_feature = os.path.join(temp,'Buffer_Zones.shp')
buffer_distance = '250 Feet'    # Set desired buffer distance
sideType = "FULL"
endType = "ROUND"
dissolveType = "NONE"
arcpy.analysis.Buffer(in_feature, out_feature, buffer_distance, sideType, endType, dissolveType)

#### Land Usage
print('3. Starting Land Use Calculations')

land_use_list = ['Residential', 'Commercial', 'Forested']
land_use_alias = ['PCT_RES', 'PCT_COM', 'PCT_FOR']

in_feature = 'LULC_RISPft.shp'

# Residential
out_feature = 'in_memory/Residential_LULC'
where_clause = "Symb_cat = 'Residential'"
arcpy.analysis.Select(in_feature, out_feature, where_clause)

# Commercial
out_feature = 'in_memory/Commercial_LULC'
where_clause = "Symb_cat = 'Commercial and Services'"
arcpy.analysis.Select(in_feature, out_feature, where_clause)

# Forested
out_feature = 'in_memory/Forested_LULC'
where_clause = "Symb_cat = 'Forest Land'"
arcpy.analysis.Select(in_feature, out_feature, where_clause)

# For loop to tabulate intersection between each land use and buffer zones, then join data into roads dataset
i = 0
for item in land_use_list:

    # Tabulate Intersection
    inZoneData = os.path.join(temp,'Buffer_Zones.shp')
    zoneField = 'FID'
    inClassData = os.path.join('in_memory', str(item) + '_LULC')
    outTable = os.path.join('in_memory', str(item) + '_tabulate')
    arcpy.analysis.TabulateIntersection(inZoneData, zoneField, inClassData, outTable)

    # Get list of field names of tabulate intersection table to use in join field
    fldLst = arcpy.ListFields(outTable)
    fldLst2 = []
    for fld in fldLst:
        fldLst2.append(fld.baseName)

    # Alter 'PERCENTAGE' field to have more meaningful name (, through Add/Calculate field operation
    in_table = os.path.join('in_memory', str(item) + '_tabulate')
    old_field = 'PERCENTAGE'
    new_field = str(land_use_alias[i])
    field_type = 'DOUBLE'
    arcpy.management.AddField(in_table, new_field, field_type)
    arcpy.management.CalculateField(in_table, new_field, '!' + old_field + '!', 'PYTHON3')

    # Join Field
    in_data = os.path.join(temp,'Final_Roads.shp')
    in_field = 'FID'
    join_table = os.path.join('in_memory', str(item) + '_tabulate')
    join_field = fldLst2[1]
    field = str(land_use_alias[i])
    arcpy.management.JoinField(in_data, in_field, join_table, join_field, field)

    i += 1

#### Impervious Surface Area
print('4. Starting Impervious Surface Area Calculations')

# Tabulate Intersection of Impervious Surface Area
inZoneData = os.path.join(temp, 'Buffer_Zones.shp')
zoneField = 'FID'
inClassData = 'Impervious_RISPft.shp'
out_table = 'in_memory/Impervious_table'
arcpy.analysis.TabulateIntersection(inZoneData, zoneField, inClassData, out_table)

# Alter 'PERCENTAGE' field to have more meaningful name (from land_use_alias list on line 68)
in_table = 'in_memory/Impervious_table'
old_field = 'PERCENTAGE'
new_field = 'PCT_IMP'
field_type = 'DOUBLE'
arcpy.management.AddField(in_table, new_field, field_type, '', '', '', new_field)
arcpy.management.CalculateField(in_table, new_field, '!' + old_field + '!', 'PYTHON3')

# Join Field
in_table = os.path.join(temp, 'Final_Roads.shp')
in_field = 'FID'
join_table = 'in_memory/Impervious_table'
join_field = fldLst2[1]
field = 'PCT_IMP'
arcpy.management.JoinField(in_table, in_field, join_table, join_field, field)

#### Canopy Coverage
print('5. Starting Canopy Coverage Calculations')

# Set null all trees that are less than 8 feet (after playing around 8 seemed to be the magic number)
in_feature = os.path.join(input_directory,'Canopy_RISPft.tif')
FalseRaster = in_feature
whereClause = "VALUE < 8"
outsetnull = arcpy.sa.SetNull(in_feature, FalseRaster, whereClause)
outsetnull.save('in_memory/Canopy_8ft')

# Execute RasterToPolygon
in_feature = 'in_memory/Canopy_8ft'
out_feature = 'in_memory/Canopy_poly'
field = "VALUE"
arcpy.conversion.RasterToPolygon(in_feature, out_feature, "NO_SIMPLIFY", field)

# Tabulate Intersection of Canopy polygons
inZoneData = os.path.join(temp, 'Buffer_Zones.shp')
zoneField = 'FID'
inClassData = 'in_memory/Canopy_poly'
out_table = 'in_memory/Canopy_table'
arcpy.analysis.TabulateIntersection(inZoneData, zoneField, inClassData, out_table)

# Alter 'PERCENTAGE' field to have more meaningful name
in_table = 'in_memory/Canopy_table'
old_field = 'PERCENTAGE'
new_field = 'PCT_CANOPY'
field_type = 'DOUBLE'
arcpy.management.AddField(in_table, new_field, field_type, '', '', '', new_field)
arcpy.management.CalculateField(in_table, new_field, '!' + old_field + '!', 'PYTHON3')

# Join Field
in_table = os.path.join(temp, 'Final_Roads.shp')
in_field = 'FID'
join_table = 'in_memory/Canopy_table'
join_field = fldLst2[1]
field = 'PCT_CANOPY'
arcpy.management.JoinField(in_table, in_field, join_table, join_field, field)

# Use Zonal Statistics to take average tree height in each buffer zone
in_feature = os.path.join(temp,'Buffer_Zones.shp')
zone_field = 'FID'
in_raster = 'in_memory/Canopy_8ft'
out_table = 'in_memory/Buffer_Canopy_table'
ignore_nodata = 'DATA'
statistics_type = 'MEAN'
arcpy.sa.ZonalStatisticsAsTable(in_feature, zone_field, in_raster, out_table, ignore_nodata, statistics_type)

# Alter 'MEAN' field to have more meaningful name
in_table = 'in_memory/Buffer_Canopy_table'
old_field = 'MEAN'
new_field = 'AVG_CANOPY_HEIGHT'
field_type = 'DOUBLE'
arcpy.management.AddField(in_table, new_field, field_type, field_length=20)
arcpy.management.CalculateField(in_table, new_field, '!' + old_field + '!', 'PYTHON3')

# Join Field
in_table = os.path.join(temp, 'Final_Roads.shp')
in_field = 'FID'
join_table = 'in_memory/Buffer_Canopy_table'
join_field =fldLst2[1]
field = 'AVG_CANOPY_HEIGHT'
arcpy.management.JoinField(in_table, in_field, join_table, join_field, field)

#### Building Density
print('6. Starting Building Density Calculations')

# Tabulate Intersection of building polygons
inZoneData = os.path.join(temp, 'Buffer_Zones.shp')
zoneField = 'FID'
inClassData = 'Buildings_RISPft.shp'
out_table = 'in_memory/Buildings_table'
arcpy.analysis.TabulateIntersection(inZoneData, zoneField, inClassData, out_table)

# Alter 'PERCENTAGE' field to have more meaningful name
in_table = 'in_memory/Buildings_table'
old_field = 'PERCENTAGE'
new_field = 'PCT_BUILDING'
field_type = 'DOUBLE'
arcpy.management.AddField(in_table, new_field, field_type, field_length=20)
arcpy.management.CalculateField(in_table, new_field, '!' + old_field + '!', 'PYTHON3')

# Join Field
in_table = os.path.join(temp, 'Final_Roads.shp')
in_field = 'FID'
join_table = 'in_memory/Buildings_table'
join_field = fldLst2[1]
field = 'PCT_BUILDING'
arcpy.management.JoinField(in_table, in_field, join_table, join_field, field)

print('All Done... Explore the Final_Roads.shp dataset in "input_directory/output_files". \n '
      'Change the symbology to see how different areas have varying road conditions.')

# Copy into Output Folder
arcpy.management.CopyFeatures(os.path.join(temp, 'Final_Roads.shp'), os.path.join(output,'Final_Roads.shp'))

# Delete Temporary Folder
if keep_temp_files == False:
    arcpy.Delete_management(os.path.join(input_directory, "temporary_files"))

# Calculate Run Time
elapsed = time.time() - start_time
elapsed = time.strftime("%M:%S.{}".format(str(elapsed % 1)[2:])[:8], time.gmtime(elapsed))
print("--- Run time (MM:SS): " + elapsed + " ---")