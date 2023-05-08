## Pollution Accumulation and Street Sweeping Tool (PASST)

### This ArcGIS toolbox tracks pollution accumulation, street sweeping events, and pollutant washoff due to rainfall across a series of roads. The toolbox includes two tools that shall be used in succession. 

#### The first tool is called 'Land Use Calculator' and requires two input files: a roads feature class and land use feature class. An output feature class is created that includes the percentage of residential, commercial, and forested land use within the area surrounding the roads. Additionally, the user can define the buffer distance, which is the amount of area surrounding the roads used to calculate the land use percentages. A default of 250 feet is used.

#### The second tool is called 'Pollutant Accumulation and Street Sweeping Tool' and requires one input file, which should be the output feature class of the 'Land Use Calculator Tool' This tool tracks the pollutant accumulation, street sweeping events, and pollutant washoff due to rainfall across the roads.


| **Variable Name**                   | **Unit**   | **Limits** | **Description**                                                                                                                |
|-------------------------------------|------------|------------|--------------------------------------------------------------------------------------------------------------------------------|
| Slope Threshold for Sweeping Events | unitless   | <td nowrap>[0.03 - 1]</td> | Function of pollution accumulation slope, dependent on buildup limit (larger values correlate to more sweeping events)         |
| Buildup Limit                       | pounds     | limitless  | Maximum amount of pollution that can accumulate on 1 curb-mi of road                                                           |
| Days to Reach Buildup Limit         | days       | limitless  | Days it will take for pollution to reach its buildup limit, for each land use (larger values correlate to slower accumulation) |
| Street Sweeper Removal Efficiency   | percentage | [0, 1]     | Efficiency of street sweepers at removing pollution (larger values correlate to more pollution removed)                        |
| Simulation Dates                    | M/D/YYYY   | past date  | Start and End dates of simulation                                                                                              |



##### -	Slope threshold (float, unitless, between 0.03 and 1)*
###### 
##### -	Buildup limit (integer, units of pounds)*
##### -	Days to reach buildup limit (integer, units of days, for each land use)*
##### -	Street sweeper removal efficiency (float, units of percentage, between 0 and 1)*
##### - Start date of simulation (M/D/YYYY)
##### - End date of simulation (M/D/YYYY)
##### * Recommended default values were given, however the user may change the values as long as they're within the limits

#### To summarize the tool:
##### 3)	Rainfall is tracked using historical rain data from the Meteostat package (please note that Meteostat must be installed in your ArcGIS interpreter. Rain data from 2022 is preselected, which means the number of days in the simulation can only be between 1 and 365, which is a user input. On days when it rains more than 0.5 inches, 90% of accumulated pollution is washed off; on days when it rains more than 0.2 inches, only 20% of pollution is washed off. Washed off pollution is tracked.
##### 4)	Street sweeping events are set up to occur once the slope of the accumulation function decreases below a certain threshold (Slope Threshold in user inputs). The slope threshold is a percentage of the maximum buildup limit. Slope threshold must be between 0.03 and 1. Pollution removed from street sweeping and number of sweeping events are tracked.
##### 5)	The tool is formulated for two Scenarios: Scenario 0 has zero sweeping events and just tracks pollutant washoff due to rain; Scenario 1 includes street sweeping and pollutant washoff due to rain. The output roads dataset and messages appear to display these metrics comparing these two Scenarios.
##### 6)	Lastly a plot using matplotlib is generated for each of the roads in the dataset.
