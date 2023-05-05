import arcpy
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
import pandas as pd
import meteostat
from datetime import datetime
import math

arcpy.env.overwriteOutput = True

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Pollution Accumulation and Street Sweeping Tool"
        self.alias = "Pollution Accumulation and Street Sweeping Tool"

        # List of tool classes associated with this toolbox
        self.tools = [PASST]


class PASST(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Pollution Accumulation and Street Sweeping Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        # Code for parameters function
        params = []
        input_roads = arcpy.Parameter(name="input_roads",
                                      displayName="Input Roads",
                                      datatype="DEFeatureClass",
                                      parameterType="Required",  # Required|Optional|Derived
                                      direction="Input",  # Input|Output
                                      )
        input_roads.value = "INPUT_DATA/Roads_final.shp"
        params.append(input_roads)

        land_use = arcpy.Parameter(name="land_use",
                                   displayName="Land Use",
                                   datatype="DEFeatureClass",
                                   parameterType="Required",  # Required|Optional|Derived
                                   direction="Input",  # Input|Output
                                   )
        land_use.values = "INPUT_DATA/LULC_RISPft.shp"
        params.append(land_use)

        output_roads = arcpy.Parameter(name="output_roads",
                                       displayName="Output Roads",
                                       datatype="DEFeatureClass",
                                       parameterType="Required",  # Required|Optional|Derived
                                       direction="Output",  # Input|Output
                                       )
        output_roads.value = "Output_roads.shp"
        params.append(output_roads)

        buffer_dist = arcpy.Parameter(name="buffer_dist",
                                      displayName="Buffer Distance (feet)",
                                      datatype="GPLong",
                                      parameterType="Required",
                                      direction="Input",  # Input|Output
                                      )
        buffer_dist.value = 250
        params.append(buffer_dist)

        days = arcpy.Parameter(name="days",
                               displayName="Days in Simulation (1 - 365)",
                               datatype="GPLong",
                               parameterType="Required",
                               direction="Input",  # Input|Output
                               )
        days.value = 365
        params.append(days)

        slope_threshold = arcpy.Parameter(name="slope_threshold",
                                          displayName="Slope Threshold for Sweeping Events (0.03 - 1)",
                                          datatype="GPDouble",
                                          parameterType="Required",
                                          direction="Input",  # Input|Output
                                          )
        slope_threshold.value = 0.1
        params.append(slope_threshold)

        QFACT1 = arcpy.Parameter(name="QFACT1",
                                 displayName="Buildup Limit (pounds)",
                                 datatype="GPLong",
                                 parameterType="Required",
                                 direction="Input",  # Input|Output
                                 )
        QFACT1.value = 100
        params.append(QFACT1)

        QFACT3_res = arcpy.Parameter(name="QFACT3_res",
                                     displayName="Days to Reach Buildup Limit (Residential)",
                                     datatype="GPLong",
                                     parameterType="Required",
                                     direction="Input",  # Input|Output
                                     )
        QFACT3_res.value = 7
        params.append(QFACT3_res)

        QFACT3_com = arcpy.Parameter(name="QFACT3_com",
                                     displayName="Days to Reach Buildup Limit (Commercial)",
                                     datatype="GPLong",
                                     parameterType="Required",
                                     direction="Input",  # Input|Output
                                     )
        QFACT3_com.value = 4
        params.append(QFACT3_com)

        QFACT3_for = arcpy.Parameter(name="QFACT3_for",
                                     displayName="Days to Reach Buildup Limit (Forest)",
                                     datatype="GPLong",
                                     parameterType="Required",
                                     direction="Input",  # Input|Output
                                     )
        QFACT3_for.value = 10
        params.append(QFACT3_for)

        REM_EFF = arcpy.Parameter(name="REM_EFF",
                                  displayName="Street Sweeper Removal Efficiency (0-1)(float)",
                                  datatype="GPDouble",
                                  parameterType="Required",
                                  direction="Input",  # Input|Output
                                  )
        REM_EFF.value = 0.85
        params.append(REM_EFF)

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        input_roads = parameters[0].valueAsText
        land_use = parameters[1].valueAsText
        output_roads = parameters[2].valueAsText
        buffer_dist = parameters[3].valueAsText
        days = parameters[4].value
        slope_threshold = parameters[5].value
        QFACT1 = parameters[6].value
        QFACT3_res = parameters[7].value
        QFACT3_com = parameters[8].value
        QFACT3_for = parameters[9].value
        REM_EFF = parameters[10].value

        # Set time period
        start = datetime(2022, 1, 1)
        end = datetime(2022, 12, 31)

        point = meteostat.Point(lat=41.7260, lon=-71.4304)
        data = meteostat.Daily(point, start, end)
        rainfall = data.fetch()
        rain = rainfall['prcp'].to_list()

        rain_in = []
        for day in rain:
            day = day * 0.03937008
            day = round(day, 2)
            rain_in.append(day)

        # Copy Features into Output Feature Class
        arcpy.management.CopyFeatures(input_roads, output_roads)

        # Create buffer zone around roads
        arcpy.AddMessage('Buffering Roads...')
        in_feature = output_roads
        out_feature = 'in_memory/Buffer_roads'
        buffer_distance = buffer_dist + ' Feet'  # Set desired buffer distance
        sideType = "FULL"
        endType = "ROUND"
        dissolveType = "NONE"
        arcpy.analysis.Buffer(in_feature, out_feature, buffer_distance, sideType, endType, dissolveType)

        # Select Residential, Commercial, and Forested Land Uses
        arcpy.AddMessage("Calculating Land Use Percentages in the Buffer Zones...")
        in_feature = land_use
        res_out_feature = 'in_memory/Residential_LULC'
        res_where_clause = "Symb_cat = 'Residential'"
        arcpy.analysis.Select(in_feature, res_out_feature, res_where_clause)
        com_out_feature = 'in_memory/Commercial_LULC'
        com_where_clause = "Symb_cat = 'Commercial and Services'"
        arcpy.analysis.Select(in_feature, com_out_feature, com_where_clause)
        for_out_feature = 'in_memory/Forest_LULC'
        for_where_clause = "Symb_cat = 'Forest Land'"
        arcpy.analysis.Select(in_feature, for_out_feature, for_where_clause)

        # Tabulate Intersection of each Land Use
        inZoneData = 'in_memory/Buffer_roads'
        zoneField = 'FID'
        res_in_feature = res_out_feature
        res_out_table = 'in_memory/Residential_table'
        arcpy.analysis.TabulateIntersection(inZoneData, zoneField, res_in_feature, res_out_table)
        com_in_feature = com_out_feature
        com_out_table = 'in_memory/Commercial_table'
        arcpy.analysis.TabulateIntersection(inZoneData, zoneField, com_in_feature, com_out_table)
        for_in_feature = for_out_feature
        for_out_table = 'in_memory/Forest_table'
        arcpy.analysis.TabulateIntersection(inZoneData, zoneField, for_in_feature, for_out_table)

        # Add New Field with more meaningful name
        arcpy.management.AddField(res_out_table, 'PCT_RES', 'DOUBLE', '', '', '', 'PCT_RES')
        arcpy.management.AddField(com_out_table, 'PCT_COM', 'DOUBLE', '', '', '', 'PCT_COM')
        arcpy.management.AddField(for_out_table, 'PCT_FOR', 'DOUBLE', '', '', '', 'PCT_FOR')

        # Calculate field to copy data over to new field
        arcpy.management.CalculateField(res_out_table, 'PCT_RES', '!PERCENTAGE!', 'PYTHON3')
        arcpy.management.CalculateField(com_out_table, 'PCT_COM', '!PERCENTAGE!', 'PYTHON3')
        arcpy.management.CalculateField(for_out_table, 'PCT_FOR', '!PERCENTAGE!', 'PYTHON3')

        arcpy.management.AddField(output_roads, 'PCT_RES', 'DOUBLE', '', '', '', 'PCT_RES')
        arcpy.management.AddField(output_roads, 'PCT_COM', 'DOUBLE', '', '', '', 'PCT_COM')
        arcpy.management.AddField(output_roads, 'PCT_FOR', 'DOUBLE', '', '', '', 'PCT_FOR')

        # Get the Land Use Percentages from Table and Update Output Roads Dataset
        res_values = [row[0] for row in arcpy.da.SearchCursor('in_memory/Residential_table', ['PCT_RES'])]
        com_values = [row[0] for row in arcpy.da.SearchCursor('in_memory/Commercial_table', ['PCT_COM'])]
        for_values = [row[0] for row in arcpy.da.SearchCursor('in_memory/Forest_table', ['PCT_FOR'])]

        with arcpy.da.UpdateCursor(output_roads, ["PCT_RES", "PCT_COM", "PCT_FOR"]) as cursor:
            for row in cursor:
                row[0] = res_values.pop(0)
                row[1] = com_values.pop(0)
                row[2] = for_values.pop(0)
                cursor.updateRow(row)

        # Search cursor to extract FID, Road Name, and Road Length
        fldLst = arcpy.ListFields(output_roads)
        fldLst2 = []
        for fld in fldLst:
            fldLst2.append(fld.baseName)
        ID = fldLst2[0]

        fields = [ID, "Road_Name", "Shape_Leng", "PCT_RES", "PCT_COM", "PCT_FOR"]  # specify fields to retrieve
        road_dict = {ID: [], 'Road_Name': [], 'Length': [], 'PCT_RES': [], 'PCT_COM': [], 'PCT_FOR': []}
        with arcpy.da.SearchCursor(output_roads, fields) as cursor:
            for row in cursor:
                fid = row[0]  # get the value of the FID field
                name = row[1]  # get road name value
                length = row[2] / 5280  # get the value of the shape_length field
                length = round(length, 2)
                road_dict[ID].append(fid)
                road_dict['Road_Name'].append(name)
                road_dict['Length'].append(length)
                road_dict['PCT_RES'].append(row[3])
                road_dict['PCT_COM'].append(row[4])
                road_dict['PCT_FOR'].append(row[5])

        land_use_list = []  # Track Dominant land use
        all_sum_washoff_0 = []  # Track total washoff pollution from scenario 0
        all_sum_swept_1 = []  # Track total swept pollution from scenario 1
        all_sweep_events_1 = []  # Track number of sweeping events from scenario 1
        all_sum_washoff_1 = []  # Track total washoff pollution from scenario 1
        all_pct_diff = []  # Track Pct washoff difference between scenarios 1 and 0

        # Subplots formatting
        fig, ax = plt.subplots(len(road_dict[ID]), sharex=True, figsize=(10, 7))
        fig.suptitle('Pollution Accumulation and Street Sweeping Tracker', fontsize=16, fontweight='bold')
        fig.text(0.04, 0.5, 'Accumulation (pounds)', ha='center', va='center', rotation='vertical')

        # Loop through each road in dataset
        for i in range(len(road_dict[ID])):
            name = road_dict['Road_Name'][i]
            length = road_dict['Length'][i]
            arcpy.AddMessage("Tracking Pollution for {0} ({1} miles)...".format(name, length))

            # Set QFACT3 = Days to reach buildup limit, dependent on dominant land use
            # QFACT3 = 4 if commercial, 7 if residential, and 10 if forested
            # The lower the QFACT3, the quicker pollution accumulates
            arcpy.management.AddField(output_roads, 'LandUse', 'TEXT', '', '', '', 'Dominant Land Use')
            if road_dict['PCT_RES'][i] >= road_dict['PCT_COM'][i] and road_dict['PCT_RES'][i] >= road_dict['PCT_FOR'][
                i]:
                QFACT3 = QFACT3_res
                land_use_list.append('Residential')
            elif road_dict['PCT_COM'][i] >= road_dict['PCT_RES'][i] and road_dict['PCT_COM'][i] >= road_dict['PCT_FOR'][
                i]:
                QFACT3 = QFACT3_com
                land_use_list.append('Commercial')
            elif road_dict['PCT_FOR'][i] >= road_dict['PCT_RES'][i] and road_dict['PCT_FOR'][i] >= road_dict['PCT_COM'][
                i]:
                QFACT3 = QFACT3_for
                land_use_list.append('Forest')

            # Pollution tracking variables
            Poll_0 = []  # Track Pollution with rain - Scenario 0 (no sweeping)
            Poll_1 = []  # Track Pollution with rain and sweeping - Scenario 1
            Poll_washoff0 = []  # Track Pollution washoff from rain - Scenario 1
            Poll_washoff1 = []  # Track Pollution washoff from rain - Scenario 1
            Poll_swept1 = []  # Track Pollution swept - Scenario 1

            # Track days for pollutant accumulation functions - days reset if sweeping or rain occurs
            d0_list = []  # Track dry/no sweep days - Scenario 0
            d0 = 0
            d1_list = []  # Track dry/no sweep days - Scenario 1
            d1 = 0

            # Track slope of pollutant accumulation function - street sweep if slope < slope_threshold*buildup_limit
            num_slope_pts = 3
            slope_threshold = slope_threshold  # percentage of buildup limit [0-1]
            slope1_list = []  # Track slope of pollutant build up - Scenario 1

            # Loop through each day of simulation - track pollution, washoff, and sweeping events for each Scenario
            for day in range(days):

                #### Track Scenario 0 Pollution - with rain; no sweeping
                Poll_0d = ((QFACT1 * d0) / (QFACT3 + d0)) * length

                # Washoff function
                if rain_in[day] > 0.5:
                    Poff_0d = 0.9 * Poll_0d
                elif rain_in[day] > 0.2:
                    Poff_0d = 0.5 * Poll_0d
                else:
                    Poff_0d = 0

                # Subtract pollution washed off and reset day counter
                if Poff_0d > 0:
                    Poll_0d = Poll_0d - Poff_0d
                    d0 = (Poll_0d * QFACT3) / (QFACT1 * length - Poll_0d) + 1
                else:
                    d0 += 1
                    d0 = math.trunc(d0)

                Poll_0d = round(Poll_0d, 2)
                Poff_0d = round(Poff_0d, 2)
                d0 = round(d0, 2)
                Poll_0.append(Poll_0d)
                Poll_washoff0.append(Poff_0d)
                d0_list.append(d0)

                #### Track Scenario 1 Pollution - with sweeping and rain
                Poll_1d = ((QFACT1 * d1) / (QFACT3 + d1)) * length

                # Washoff function
                if rain_in[day] > 0.5:
                    Poff_1d = 0.9 * Poll_1d
                elif rain_in[day] > 0.2:
                    Poff_1d = 0.5 * Poll_1d
                else:
                    Poff_1d = 0

                # Sweeping function
                if day > 2:
                    # slope = (y2 - y1) / (x2 - x1)
                    slope1 = (Poll_1d - Poll_1[day - num_slope_pts]) / num_slope_pts
                    if rain_in[day] > 0:
                        Pswept_1d = 0
                    else:
                        # Sweep if slope is less than 100
                        if slope_threshold * QFACT1 > slope1 > 2:
                            Pswept_1d = REM_EFF * Poll_1d
                        else:
                            Pswept_1d = 0
                else:
                    slope1 = 0
                    Pswept_1d = 0

                # Subtract pollution washed off and reset day counter
                if Poff_1d > 0:
                    Poll_1d = Poll_1d - Poff_1d

                # Subtract pollution swept off and reset day counter
                if Pswept_1d > 0:
                    Poll_1d = Poll_1d - Pswept_1d
                    d1 = (Poll_1d * QFACT3) / (QFACT1 * length - Poll_1d) + 1
                elif Poff_1d > 0:
                    Poll_1d = Poll_1d - Pswept_1d
                    d1 = (Poll_1d * QFACT3) / (QFACT1 * length - Poll_1d) + 1
                else:
                    d1 += 1
                    d1 = math.trunc(d1)

                Poll_1d = round(Poll_1d, 2)
                Pswept_1d = round(Pswept_1d, 2)
                Poff_1d = round(Poff_1d, 2)
                d1 = round(d1, 2)
                slope1 = round(slope1, 2)
                Poll_1.append(Poll_1d)
                Poll_swept1.append(Pswept_1d)
                Poll_washoff1.append(Poff_1d)
                d1_list.append(d1)
                slope1_list.append(slope1)

                df_0 = pd.DataFrame(columns=['Poll_0', 'Poll_Washoff0', 'D0'])
                df_1 = pd.DataFrame(columns=['Poll_1', 'Poll_Swept1', 'Poll_Washoff1', 'Slope1', 'D1'])

                df_0['Poll_0'] = Poll_0
                df_0['Poll_Washoff0'] = Poll_washoff0
                df_0['D0'] = d0_list

                df_1['Poll_1'] = Poll_1
                df_1['Poll_Swept1'] = Poll_swept1
                df_1['Poll_Washoff1'] = Poll_washoff1
                df_1['Slope1'] = slope1_list
                df_1['D1'] = d1_list

            #### Calculate Metrics

            # 1. Calculate sum of pollution washed off in Scenario 0
            sum_washoff_0 = 0
            for day in Poll_washoff0:
                sum_washoff_0 += day
            sum_washoff_0 = round(sum_washoff_0, 2)
            all_sum_washoff_0.append(sum_washoff_0)
            arcpy.AddMessage('    - Sum of Pollution washed off (Scenario 0): {0} pounds'.format(sum_washoff_0))

            # 2. Calculate sum of pollution removed in Scenario 1
            sum_swept_1 = 0

            for day in Poll_swept1:
                sum_swept_1 += day
            sum_swept_1 = round(sum_swept_1, 2)
            all_sum_swept_1.append(sum_swept_1)
            arcpy.AddMessage('    - Sum of Pollution swept off (Scenario 1): {0} pounds'.format(sum_swept_1))

            # 3. Calculate total number of sweeping events
            count_sweep1 = 0
            for day in Poll_swept1:
                if day > 0:
                    count_sweep1 += 1
            all_sweep_events_1.append(count_sweep1)
            arcpy.AddMessage('    - Total number of sweeping events (Scenario 1): {0}'.format(count_sweep1))

            # 4. Calculate sum of pollution washed off in Scenario 1
            sum_washoff_1 = 0
            for day in Poll_washoff1:
                sum_washoff_1 += day
            sum_washoff_1 = round(sum_washoff_1, 2)
            all_sum_washoff_1.append(sum_washoff_1)
            arcpy.AddMessage('    - Sum of Pollution washed off (Scenario 1): {0} pounds'.format(sum_washoff_1))

            # 4. Percent difference of washoff between Scenario 0 and 1

            pct_diff = (sum_washoff_1 - sum_washoff_0) / sum_washoff_0 * 100
            pct_diff = round(pct_diff, 2)
            all_pct_diff.append(pct_diff)
            arcpy.AddMessage('    - Reduction of Pollution washoff from Scenario 0 to 1: {0}%'.format(pct_diff))

            # Plot results in subplots
            ax[i].plot(Poll_1, label='Accumulation', color='GREEN')
            ax[i].bar(df_1.index, Poll_swept1, label='Swept Pollution', color='RED')
            ax[i].bar(df_1.index, Poll_washoff1, label='Washed off Pollution', color='BLUE')
            ax[i].set_title(name)

        ax[i].legend(loc='lower center', bbox_to_anchor=(0.5, -1), ncol=3)
        ax[i].set_xlabel('Days')
        # Save Plot
        plt.subplots_adjust(top=0.85, hspace=0.4)
        plt.savefig('PollutionTracker_plot2.tif', dpi=300)
        plt.close()

        # Add the fields to the feature class
        arcpy.AddField_management(output_roads, 'LandUse', "TEXT")
        arcpy.AddField_management(output_roads, 'P_WOff_0', "FLOAT")
        arcpy.AddField_management(output_roads, 'P_WOff_1', "FLOAT")
        arcpy.AddField_management(output_roads, 'P_Swept_1', "FLOAT")
        arcpy.AddField_management(output_roads, 'Sw_Events', "FLOAT")
        arcpy.AddField_management(output_roads, 'WOff_Diff', "FLOAT")

        fields = ['LandUse', 'P_WOff_0', 'P_WOff_1', 'P_Swept_1', 'Sw_Events', 'WOff_Diff']
        with arcpy.da.UpdateCursor(output_roads, fields) as cursor:
            for row in cursor:
                row[0] = land_use_list.pop(0)
                row[1] = all_sum_washoff_0.pop(0)
                row[2] = all_sum_washoff_1.pop(0)
                row[3] = all_sum_swept_1.pop(0)
                row[4] = all_sweep_events_1.pop(0)
                row[5] = all_pct_diff.pop(0)

                cursor.updateRow(row)

        return


# This code block allows you to run your code in a test-mode within PyCharm, i.e. you do not have to open the tool in
# ArcMap. This works best for a "single tool" within the Toolbox.
def main():
    tool = PASST()  # i.e. what you have called your tool class: class Clippy(object):
    tool.execute(tool.getParameterInfo(), None)


if __name__ == '__main__':
    main()
