# This tool utilizes the BUFFER and TABULATE INTERSECTION tools to calculate the percent land use cover for the area
# surrounding a road. PROJECT and SELECT tools were also used for formatting purposes. The required data includes
# Roads, Land use, and Municipality feature classes. All data was downloaded from the RIGIS website.

import arcpy
arcpy.env.overwriteOutput = True

###############################    UPDATE WORKSPACE HERE   ###############################
arcpy.env.workspace = r"C:\Users\OpenTron\Documents\NRS528\Coding Challenges\CC_04\DATA"

### STEP 1: Project everything in Rhode Island State Plane, with units of US Feet

# Project roads
in_dataset = r'RIDOT_Roads__2016_.shp'
out_dataset = r'Roads_RISPft.shp'
out_coor_system = arcpy.SpatialReference('NAD 1983 StatePlane Rhode Island FIPS 3800 (US Feet)')
arcpy.Project_management(in_dataset, out_dataset, out_coor_system)

# Project LULC
in_dataset = r'PLAN_Land_Cover_Use_2020.shp'
out_dataset = r'LULC_RISPft.shp'
arcpy.Project_management(in_dataset, out_dataset, out_coor_system)

# Project Muncipalities
in_dataset = r'Municipalities__1997_.shp'
out_dataset = r'Municipalities_RISPft.shp'
arcpy.Project_management(in_dataset, out_dataset, out_coor_system)

### STEP 2: Set the extent. The desired study area for this tool is Warwick, RI.

# Select study area (Warwick
in_features = r'Municipalities_RISPft.shp'
out_feature_class = r'StudyArea.shp'
where_clause = "NAME = 'WARWICK'"
arcpy.analysis.Select(in_features, out_feature_class, where_clause)

# Use describe to calculate Xmin, Xmax, Ymin, Ymax extents
desc = arcpy.Describe(out_feature_class)
Xmin = desc.extent.XMin
Ymin = desc.extent.YMin
Xmax = desc.extent.XMax
Ymax = desc.extent.YMax

# Set arcpy.env.extent
arcpy.env.extent = arcpy.Extent(Xmin, Ymin, Xmax, Ymax)

### STEP 3: Set roads study area to be state maintained roads (juris = 2 or 3) using select tool
in_features = r'Roads_RISPft.shp'
out_feature_class = r'Roads_studyarea.shp'
where_clause = "JURIS = 2 Or JURIS = 3"
arcpy.analysis.Select(in_features, out_feature_class, where_clause)

### STEP 4: Create buffer zone around roads, which will be used to tabulate intersection
in_features = r'Roads_studyarea.shp'
out_feature_class = r'Roads_buffer.shp'
buffer_distance = '250 Feet'
sideType = "FULL"
endType = "ROUND"
dissolveType = "NONE"
arcpy.analysis.Buffer(in_features, out_feature_class, buffer_distance, sideType, endType, dissolveType)

### STEP 5: Select desired land use datasets, in this case only Residential, Commercial, and Forested

# Residential
in_features = r'LULC_RISPft.shp'
out_feature_class = r'Residential_LULC.shp'
where_clause = "Symb_cat = 'Residential'"
arcpy.analysis.Select(in_features, out_feature_class, where_clause)

# Commercial
in_features = r'LULC_RISPft.shp'
out_feature_class = r'Commercial_LULC.shp'
where_clause = "Symb_cat = 'Commercial and Services'"
arcpy.analysis.Select(in_features, out_feature_class, where_clause)

# Forested
in_features = r'LULC_RISPft.shp'
out_feature_class = r'Forested_LULC.shp'
where_clause = "Symb_cat = 'Forest Land'"
arcpy.analysis.Select(in_features, out_feature_class, where_clause)

### STEP 6: Tabulate Intersection for each land use feature class and add result back to ROADS dataset

# Simplified process by using for loops for the following land use classes
land_use_list = ['Residential', 'Commercial', 'Forested']
land_use_alias = ['Pct_res', 'Pct_com', 'Pct_for']
i = 0
for item in land_use_list:

    # Tabulate Intersection
    inZoneData = r"Roads_buffer.shp"
    zoneField = "OBJECTID"
    inClassData = str(item) + "_LULC.shp"
    outTable = str(item) + "_tabulate.dbf"
    processingCellSize = 1
    arcpy.analysis.TabulateIntersection(inZoneData, zoneField, inClassData, outTable)

    # Alter 'PERCENTAGE' field to have more meaningful name, through Add/Calculate field operation
    # Alter field does not work for .dbf
    in_table = str(item) + '_tabulate.dbf'
    old_field = 'PERCENTAGE'
    new_field = str(land_use_alias[i])
    field_type = 'DOUBLE'
    arcpy.management.AddField(in_table, new_field, field_type, '', '', '', new_field)
    arcpy.management.CalculateField(in_table, new_field, '!' + old_field + '!', 'PYTHON3')

    # Join Field
    in_data = r'Roads_studyarea.shp'
    in_field = 'OBJECTID'
    join_table = str(item) + '_tabulate.dbf'
    join_field = 'OBJECTID_1'
    field = str(land_use_alias[i])
    arcpy.management.JoinField(in_data, in_field, join_table, join_field, field)

    i += 1

### STEP 7: Visualize Roads_studyarea.shp dataset to see which roads are residential, commercial, or forested