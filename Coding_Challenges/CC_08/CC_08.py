########################
# The following script builds on my Midterm, in which metrics that summarize the area around a road are calculated.
# The results of this work will assist a research project to develop an enhanced street sweeping program, which will
# optimize the location and frequency of street sweeping. The following metrics are calculated as
# percentage of area within a buffer zone around each road segment:

#     1. Percent Land Usage - Residential, Commercial, and Forested
#     2. Percent Impervious Surface Area
#     3. Percent Canopy Coverage (and Average Canopy Height)
#     4. Percent Building Coverage
#     5. Binary Bike Path
#     6. Proximity to Sweeper Parking Locations (ex. Fire Stations, Park and Rides)

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
########################

import time
# Track run time
start_time = time.time()

import arcpy
import os
import pandas as pd

###### USER INPUTS ######
input_directory = r"C:\Users\OpenTron\Documents\NRS528\Coding Challenges\CC_08\DATA"
###### USER INPUTS ######

# Set up arcpy environment
arcpy.env.overwriteOutput = True
arcpy.env.workspace = input_directory

# Set up temporary and output directories
keep_temp_files = False  # Change to true if you want to keep temp files
if not os.path.exists(os.path.join(input_directory, "temporary_files")):
    os.mkdir(os.path.join(input_directory, "temporary_files"))
if not os.path.exists(os.path.join(input_directory, "output_files")):
    os.mkdir(os.path.join(input_directory, "output_files"))
temp = 'temporary_files'
output = 'output_files'

def road_prioritization_tool(town):         #### RUN FUNCTION STARTING ON LINE 370
    town2 = town.replace(" ", "")

    #### Setting up study area, roads and buffer zones
    print('1. Setting Up Study Area, Roads, and Buffer Zones for ' + town)

    in_feature = r'Municipalities_RISPft.shp'
    out_feature = os.path.join(temp, 'Study_Area_' + town2 + '.shp')

    where_clause = "NAME = '" + town + "'"
    arcpy.analysis.Select(in_feature, out_feature, where_clause)

    # Set extent base on study area
    desc = arcpy.Describe(out_feature)
    arcpy.env.extent = arcpy.Extent(desc.extent.XMin, desc.extent.YMin, desc.extent.XMax, desc.extent.YMax)

    # Select state roads
    in_feature = r'Roads_RISPft.shp'
    out_feature = 'in_memory/State_Roads_' + town2
    where_clause = "JURIS = 2 Or JURIS = 3"     # State maintained roads have jurisdiction of 2 or 3
    arcpy.analysis.Select(in_feature, out_feature, where_clause)

    # Clip to municipality borders
    in_feature = 'in_memory/State_Roads_' + town2
    clip_feature = os.path.join(temp, 'Study_Area_' + town2 + '.shp')
    out_feature = 'in_memory/Roads_Clipped_' + town2
    arcpy.analysis.Clip(in_feature, clip_feature, out_feature)

    # Dissolve and format roads to have 0.1 mile segments
    in_feature = 'in_memory/Roads_Clipped_' + town2
    out_feature = 'in_memory/Roads_Dissolved_' + town2
    arcpy.management.Dissolve(in_feature, out_feature)

    # Generate points along line that are 0.1 miles apart
    in_feature = 'in_memory/Roads_Dissolved_' + town2
    out_feature = 'in_memory/Roads_Points_' + town2
    distance = '0.1 miles'
    arcpy.management.GeneratePointsAlongLines(in_feature, out_feature, 'DISTANCE', distance, Include_End_Points='END_POINTS')

    # Split line at points - this will create your final roads dataset
    in_feature = 'in_memory/Roads_Dissolved_' + town2
    point_feature = 'in_memory/Roads_Points_' + town2
    out_feature = os.path.join(temp,'Final_Roads_' + town2 +'.shp')
    search_radius = '50 feet'
    arcpy.management.SplitLineAtPoint(in_feature, point_feature, out_feature, search_radius)

    # Create buffer zone around roads
    in_feature = out_feature
    out_feature = os.path.join(temp,'Buffer_Zones_' + town2 + '.shp')
    buffer_distance = '250 Feet'    # Set desired buffer distance
    sideType = "FULL"
    endType = "ROUND"
    dissolveType = "NONE"
    arcpy.analysis.Buffer(in_feature, out_feature, buffer_distance, sideType, endType, dissolveType)

    #### Land Usage
    print('2. Starting Land Use Calculations for ' + town)

    land_use_list = ['Residential', 'Commercial', 'Forested']
    land_use_alias = ['PCT_RES', 'PCT_COM', 'PCT_FOR']

    in_feature = 'LULC_RISPft.shp'

    # Residential
    out_feature = 'in_memory/Residential_LULC_' + town2
    where_clause = "Symb_cat = 'Residential'"
    arcpy.analysis.Select(in_feature, out_feature, where_clause)

    # Commercial
    out_feature = 'in_memory/Commercial_LULC_' + town2
    where_clause = "Symb_cat = 'Commercial and Services'"
    arcpy.analysis.Select(in_feature, out_feature, where_clause)

    # Forested
    out_feature = 'in_memory/Forested_LULC_' + town2
    where_clause = "Symb_cat = 'Forest Land'"
    arcpy.analysis.Select(in_feature, out_feature, where_clause)

    # For loop to tabulate intersection between each land use and buffer zones, then join data into roads dataset
    i = 0
    for item in land_use_list:

        # Tabulate Intersection
        inZoneData = os.path.join(temp,'Buffer_Zones_' + town2 + '.shp')
        zoneField = 'FID'
        inClassData = os.path.join('in_memory', str(item) + '_LULC_' + town2)
        outTable = os.path.join('in_memory', str(item) + '_tabulate_' + town2)
        arcpy.analysis.TabulateIntersection(inZoneData, zoneField, inClassData, outTable)

        # Get list of field names of tabulate intersection table to use in join field
        fldLst = arcpy.ListFields(outTable)
        fldLst2 = []
        for fld in fldLst:
            fldLst2.append(fld.baseName)

        # Alter 'PERCENTAGE' field to have more meaningful name (, through Add/Calculate field operation
        in_table = os.path.join('in_memory', str(item) + '_tabulate_' + town2)
        old_field = 'PERCENTAGE'
        new_field = str(land_use_alias[i])
        field_type = 'DOUBLE'
        arcpy.management.AddField(in_table, new_field, field_type)
        arcpy.management.CalculateField(in_table, new_field, '!' + old_field + '!', 'PYTHON3')

        # Join Field
        in_data = os.path.join(temp,'Final_Roads_' + town2 +'.shp')
        in_field = 'FID'
        join_table = os.path.join('in_memory', str(item) + '_tabulate_' + town2)
        join_field = fldLst2[1]
        field = str(land_use_alias[i])
        arcpy.management.JoinField(in_data, in_field, join_table, join_field, field)

        i += 1

    #### Impervious Surface Area
    print('3. Starting Impervious Surface Area Calculations for ' + town)

    # Tabulate Intersection of Impervious Surface Area
    inZoneData = os.path.join(temp,'Buffer_Zones_' + town2 + '.shp')
    zoneField = 'FID'
    inClassData = 'Impervious_RISPft.shp'
    out_table = 'in_memory/Impervious_table_' + town2
    arcpy.analysis.TabulateIntersection(inZoneData, zoneField, inClassData, out_table)

    # Alter 'PERCENTAGE' field to have more meaningful name (from land_use_alias list on line 68)
    in_table = 'in_memory/Impervious_table_' + town2
    old_field = 'PERCENTAGE'
    new_field = 'PCT_IMP'
    field_type = 'DOUBLE'
    arcpy.management.AddField(in_table, new_field, field_type, '', '', '', new_field)
    arcpy.management.CalculateField(in_table, new_field, '!' + old_field + '!', 'PYTHON3')

    # Join Field
    in_table = os.path.join(temp,'Final_Roads_' + town2 +'.shp')
    in_field = 'FID'
    join_table = 'in_memory/Impervious_table_' + town2
    join_field = fldLst2[1]
    field = 'PCT_IMP'
    arcpy.management.JoinField(in_table, in_field, join_table, join_field, field)

    #### Canopy Coverage
    print('4. Starting Canopy Coverage Calculations for ' + town)

    # Set null all trees that are less than 8 feet (after playing around 8 seemed to be the magic number)
    in_feature = os.path.join(input_directory,'Canopy_RISPft.tif')
    FalseRaster = in_feature
    whereClause = "VALUE < 8"
    outsetnull = arcpy.sa.SetNull(in_feature, FalseRaster, whereClause)

    # Execute RasterToPolygon
    in_feature = outsetnull
    out_feature = 'in_memory/Canopy_poly_' + town2
    field = "VALUE"
    arcpy.conversion.RasterToPolygon(in_feature, out_feature, "NO_SIMPLIFY", field)

    # Tabulate Intersection of Canopy polygons
    inZoneData = os.path.join(temp, 'Buffer_Zones_' + town2 + '.shp')
    zoneField = 'FID'
    inClassData = 'in_memory/Canopy_poly_' + town2
    out_table = 'in_memory/Canopy_table_' + town2
    arcpy.analysis.TabulateIntersection(inZoneData, zoneField, inClassData, out_table)

    # Alter 'PERCENTAGE' field to have more meaningful name
    in_table = 'in_memory/Canopy_table_' + town2
    old_field = 'PERCENTAGE'
    new_field = 'PCT_CANOPY'
    field_type = 'DOUBLE'
    arcpy.management.AddField(in_table, new_field, field_type, '', '', '', new_field)
    arcpy.management.CalculateField(in_table, new_field, '!' + old_field + '!', 'PYTHON3')

    # Join Field
    in_table = os.path.join(temp, 'Final_Roads_' + town2 + '.shp')
    in_field = 'FID'
    join_table = 'in_memory/Canopy_table_' + town2
    join_field = fldLst2[1]
    field = 'PCT_CANOPY'
    arcpy.management.JoinField(in_table, in_field, join_table, join_field, field)

    # Use Zonal Statistics to take average tree height in each buffer zone
    in_feature = os.path.join(temp, 'Buffer_Zones_' + town2 + '.shp')
    zone_field = 'FID'
    in_raster = outsetnull
    out_table = 'in_memory/Buffer_Canopy_table_' + town2
    ignore_nodata = 'DATA'
    statistics_type = 'MEAN'
    arcpy.sa.ZonalStatisticsAsTable(in_feature, zone_field, in_raster, out_table, ignore_nodata, statistics_type)

    # Alter 'MEAN' field to have more meaningful name
    in_table = 'in_memory/Buffer_Canopy_table_' + town2
    old_field = 'MEAN'
    new_field = 'AVG_CANOPY_HEIGHT'
    field_type = 'DOUBLE'
    arcpy.management.AddField(in_table, new_field, field_type, field_length=20)
    arcpy.management.CalculateField(in_table, new_field, '!' + old_field + '!', 'PYTHON3')

    # Join Field
    in_table = os.path.join(temp, 'Final_Roads_' + town2 + '.shp')
    in_field = 'FID'
    join_table = 'in_memory/Buffer_Canopy_table_' + town2
    join_field = fldLst2[1]
    field = 'AVG_CANOPY_HEIGHT'
    arcpy.management.JoinField(in_table, in_field, join_table, join_field, field)

    #### Building Density
    print('5. Starting Building Density Calculations for ' + town)

    # Tabulate Intersection of building polygons
    inZoneData = os.path.join(temp, 'Buffer_Zones_' + town2 + '.shp')
    zoneField = 'FID'
    inClassData = 'Buildings_RISPft.shp'
    out_table = 'in_memory/Buildings_table_' + town2
    arcpy.analysis.TabulateIntersection(inZoneData, zoneField, inClassData, out_table)

    # Alter 'PERCENTAGE' field to have more meaningful name
    in_table = 'in_memory/Buildings_table_' + town2
    old_field = 'PERCENTAGE'
    new_field = 'PCT_BUILDING'
    field_type = 'DOUBLE'
    arcpy.management.AddField(in_table, new_field, field_type, field_length=20)
    arcpy.management.CalculateField(in_table, new_field, '!' + old_field + '!', 'PYTHON3')

    # Join Field
    in_table = os.path.join(temp, 'Final_Roads_' + town2 + '.shp')
    in_field = 'FID'
    join_table = 'in_memory/Buildings_table_' + town2
    join_field = fldLst2[1]
    field = 'PCT_BUILDING'
    arcpy.management.JoinField(in_table, in_field, join_table, join_field, field)

    #### Bike Paths
    print('6. Starting Bike Path Calculations for ' + town)

    # Snap Bike Paths to Roads
    inFeature = 'BikePaths_RISPft.shp'
    snap_feature = os.path.join(temp, 'Final_Roads_' + town2 + '.shp')
    arcpy.edit.Snap(inFeature, [[snap_feature, "EDGE", "50 Feet"]])

    # Make Feature Layer
    in_feature = 'BikePaths_RISPft.shp'
    out_feature = 'in_memory/BikePaths_snapped'
    arcpy.management.MakeFeatureLayer(in_feature, out_feature)

    # Spatial Join
    in_feature = os.path.join(temp, 'Final_Roads_' + town2 + '.shp')
    join_feature = 'in_memory/BikePaths_snapped'
    out_feature = 'in_memory/BikePaths_SJ_' + town2
    join_operation = 'JOIN_ONE_TO_MANY'
    join_type = 'KEEP_ALL'
    field_mapping = 'Count'
    match_option = 'SHARE_A_LINE_SEGMENT_WITH'
    arcpy.analysis.SpatialJoin(in_feature, join_feature, out_feature, join_operation=join_operation, join_type=join_type,
                               field_mapping=field_mapping, match_option=match_option)

    # Alter field to have more meaningful name
    in_feature = 'in_memory/BikePaths_SJ_' + town2
    old_field = 'Join_Count'
    field_type = 'Short'
    new_field = 'BikePath'
    arcpy.management.AddField(in_feature, new_field, field_type, field_length=20)
    arcpy.management.CalculateField(in_feature, new_field, '!' + old_field + '!', 'PYTHON3')

    # Join field
    in_table = os.path.join(temp, 'Final_Roads_' + town2 + '.shp')
    in_field = 'FID'
    join_table = 'in_memory/BikePaths_SJ_' + town2
    join_field = fldLst2[1]
    field = 'BikePath'
    arcpy.management.JoinField(in_table, in_field, join_table, join_field, field)

    #### Sweeper Parking
    print('7. Determining Distance from Sweeper Stations ' + town)

    # Fire Stations
    in_feature = os.path.join(temp, 'Final_Roads_' + town2 + '.shp')
    near_feature = 'FireStations.shp'
    field_names = "NEAR_FID FIRE_ID;NEAR_DIST FIRE_DIST"
    arcpy.analysis.Near(in_feature, near_feature, None, "NO_LOCATION", "NO_ANGLE", "PLANAR", field_names=field_names)

    # Park and Rides
    in_feature = os.path.join(temp, 'Final_Roads_' + town2 + '.shp')
    near_feature = 'ParkAndRides.shp'
    field_names = "NEAR_FID PaR_ID;NEAR_DIST PaR_DIST"
    arcpy.analysis.Near(in_feature, near_feature, None, "NO_LOCATION", "NO_ANGLE", "PLANAR", field_names=field_names)

    #### Post Processing

    # Copy into Output Folder
    arcpy.management.CopyFeatures(os.path.join(temp, 'Final_Roads_' + town2 + '.shp'), os.path.join(output,'Final_Roads_' + town2 + '.shp'))

    # Delete Temporary Folder
    if keep_temp_files == False:
        arcpy.Delete_management(os.path.join(input_directory, "temporary_files"))

    # Print Table As Dataframe
    def table_to_data_frame(in_table, input_fields=None, where_clause=None):
        """Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
        input fields using an arcpy.da.SearchCursor."""
        OIDFieldName = arcpy.Describe(in_table).OIDFieldName
        if input_fields:
            final_fields = [OIDFieldName] + input_fields
        else:
            final_fields = [field.name for field in arcpy.ListFields(in_table)]
        data = [row for row in arcpy.da.SearchCursor(in_table, final_fields, where_clause=where_clause)]
        fc_dataframe = pd.DataFrame(data, columns=final_fields)
        fc_dataframe = fc_dataframe.set_index(OIDFieldName, drop=True)

        return fc_dataframe

    print("...All Done. Output Feature Class Length: " + str(len(table_to_data_frame(os.path.join(output,'Final_Roads_' + town2 +'.shp')))))

# study_area = ['CUMBERLAND', 'WOONSOCKET', 'NORTH SMITHFIELD', 'BURRILLVILLE', 'GLOCESTER',
#               'PAWTUCKET', 'NORTH PROVIDENCE', 'PROVIDENCE', 'EAST PROVIDENCE',
#               'FOSTER', 'WARWICK', 'WARREN', 'WEST WARWICK', 'COVENTRY', 'BRISTOL',
#               'TIVERTON', 'PORTSMOUTH', 'EAST GREENWICH', 'WEST GREENWICH', 'NORTH KINGSTOWN', 'EXETER', 'JAMESTOWN',
#               'RICHMOND', 'LITTLE COMPTON', 'MIDDLETOWN', 'HOPKINTON', 'SOUTH KINGSTOWN', 'NEWPORT', 'NARRAGANSETT',
#               'CHARLESTOWN', 'WESTERLY', 'NEW SHOREHAM', 'LINCOLN', 'SMITHFIELD', 'CENTRAL FALLS',
#               'JOHNSTON', 'SCITUATE', 'CRANSTON', 'BARRINGTON']

##### Uncomment 1 line to run road prioritization tool --- only works for one town at a time for some reason... not sure why

road_prioritization_tool("CUMBERLAND")
# road_prioritization_tool("WOONSOCKET")
# road_prioritization_tool("NORTH SMITHFIELD")
# road_prioritization_tool("BURRILLVILLE")
# road_prioritization_tool("GLOCESTER")
# road_prioritization_tool("PAWTUCKET")
# road_prioritization_tool("NORTH PROVIDENCE")
# road_prioritization_tool("PROVIDENCE")
# road_prioritization_tool("EAST PROVIDENCE")
# road_prioritization_tool("FOSTER")
# road_prioritization_tool("WARWICK")
# road_prioritization_tool("WARREN")
# road_prioritization_tool("WEST WARWICK")
# road_prioritization_tool("COVENTRY")
# road_prioritization_tool("BRISTOL")
# road_prioritization_tool("TIVERTON")
# road_prioritization_tool("PORTSMOUTH")
# road_prioritization_tool("EAST GREENWICH")
# road_prioritization_tool("WEST GREENWICH")
# road_prioritization_tool("NORTH KINGSTOWN")
# road_prioritization_tool("EXETER")
# road_prioritization_tool("JAMESTOWN")
# road_prioritization_tool("RICHMOND")
# road_prioritization_tool("LITTLE COMPTON")
# road_prioritization_tool("MIDDLETOWN")
# road_prioritization_tool("HOPKINTON")
# road_prioritization_tool("SOUTH KINGSTOWN")
# road_prioritization_tool("NEWPORT")
# road_prioritization_tool("NARRAGANSETT")
# road_prioritization_tool("CHARLESTOWN")
# road_prioritization_tool("WESTERLY")
# road_prioritization_tool("NEW SHOREHAM")
# road_prioritization_tool("LINCOLN")
# road_prioritization_tool("SMITHFIELD")
# road_prioritization_tool("CENTRAL FALLS")
# road_prioritization_tool("JOHNSTON")
# road_prioritization_tool("SCITUATE")
# road_prioritization_tool("CRANSTON")
# road_prioritization_tool("BARRINGTON")

elapsed = time.time() - start_time
elapsed = time.strftime("%M:%S.{}".format(str(elapsed % 1)[2:])[:8], time.gmtime(elapsed))
print("--- Run time (MM:SS) for: " + elapsed + " ---")

