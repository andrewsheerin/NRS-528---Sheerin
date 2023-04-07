# Coding Challenge 9
# In this coding challenge, your objective is to utilize the arcpy.da module to undertake some basic partitioning of your dataset. In this coding challenge, I want you to work with the Forest Health Works dataset from RI GIS (I have provided this as a downloadable ZIP file in this repository).
#
# Using the arcpy.da module (yes, there are other ways and better tools to do this), I want you to extract all sites that have a photo of the invasive species (Field: PHOTO) into a new Shapefile, and do some basic counts of the dataset. In summary, please addressing the following:
#   1. Count how many individual records have photos, and how many do not (2 numbers), print the results.
#   2. Count how many unique species there are in the dataset, print the result.
#   3. Generate two shapefiles, one with photos and the other without.

###############################
import arcpy
import os

#### USER INPUT ####
input_directory = r'C:\Users\OpenTron\Documents\NRS528\Coding Challenges\CC_09\DATA'
#### USER INPUT ####

# Setup environment
arcpy.env.workspace = input_directory
arcpy.env.overwriteOutput = True

if not os.path.exists(os.path.join(input_directory, "output_files")):
    os.mkdir(os.path.join(input_directory, "output_files"))
output = 'output_files'

# Set input and output shapefile names
input_shp = 'RI_Forest_Health_Works_Project%3A_Points_All_Invasives.shp'

# Count records with photos
count_with_photos = 0
where_clause_with = "photo = 'y'"
with arcpy.da.SearchCursor(input_shp, "photo", where_clause_with) as cursor:
    for row in cursor:
        count_with_photos += 1

# Count records without photos
count_wo_photos = 0
where_clause_wo = "photo = ''"
with arcpy.da.SearchCursor(input_shp, "photo", where_clause_wo) as cursor:
    for row in cursor:
        count_wo_photos += 1

print(f"Number of records with photos: {count_with_photos}")
print(f"Number of records without photos: {count_wo_photos}")

# Count the number of unique species
unique_species = []
with arcpy.da.SearchCursor(input_shp, "Species") as cursor:
    for row in cursor:
        if row[0] not in unique_species:
            unique_species.append(row[0])

print(f"Number of unique species: {len(unique_species)}")

# Create two separate feature layers for sites with and without photos
arcpy.MakeFeatureLayer_management(input_shp, "Sites_with_photos", where_clause_with)
arcpy.MakeFeatureLayer_management(input_shp, "Sites_wo_photos", where_clause_wo)

# Copy the feature layers to create separate output shapefiles
with_photos_shp = 'Forest_withPhotos.shp'
wo_photos_shp = 'Forest_woPhotos.shp'

arcpy.management.CopyFeatures("Sites_with_photos", os.path.join(output, with_photos_shp))
arcpy.management.CopyFeatures("Sites_wo_photos", os.path.join(output, wo_photos_shp))

print('All Done... Output shapefiles created')