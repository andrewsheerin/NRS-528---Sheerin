## Pollution Accumulation and Street Sweeping Tool (PASST)

### This ArcGIS toolbox tracks pollution accumulation, street sweeping events, and pollutant washoff due to rainfall across a series of roads. The toolbox includes two tools that shall be used in succession. 

#### The first tool is called 'Land Use Calculator' and requires two input files: a roads feature class and land use feature class. An output feature class is created that includes the percentage of residential, commercial, and forested land use within the area surrounding the roads. Additionally, the user can define the buffer distance, which is the amount of area surrounding the roads used to calculate the land use percentages. A default of 250 feet is used.

#### The second tool is called 'Pollutant Accumulation and Street Sweeping Tool' or PASST and requires one input file, which should be the output feature class of the 'Land Use Calculator Tool' This tool tracks the pollutant accumulation, street sweeping events, and pollutant washoff due to rainfall across the roads. The following tool parameters have supplied recommended values, however can be adjusted.

| **Variable Name**                   | **Unit**   | **Limits** | **Description**                                                                                                                |
|-------------------------------------|------------|------------|--------------------------------------------------------------------------------------------------------------------------------|
| Slope Threshold for Sweeping Events | unitless   | [0.03, 1] | Function of pollution accumulation slope, dependent on buildup limit (larger values correlate to more sweeping events)         |
| Buildup Limit                       | pounds     | limitless  | Maximum amount of pollution that can accumulate on 1 curb-mi of road                                                           |
| Days to Reach Buildup Limit         | days       | limitless  | Days it will take for pollution to reach its buildup limit, for each land use (larger values correlate to slower accumulation) |
| Street Sweeper Removal Efficiency   | percentage | [0, 1]     | Efficiency of street sweepers at removing pollution (larger values correlate to more pollution removed)                        |
| Simulation Dates                    | M/D/YYYY   | past date  | Start and End dates of simulation      

#### PASST tracks the pollutant accumulation and street sweeping for two scenarios: Scenario 0 has no street sweeping events and simply calculates the pollutant washoff due to rainfall; Scenario 1 does include street sweepign events, dependent on the user's  inputted parameters. The results given compare pollution tracking between Scenario 0 and Scenario 1. The outputed roads feature class includes the following information: percentage of residential, commercial, and forested land uses (PCT_RES, PCT_COM, and PCT_FOR, respectively), Sum of pollution washed off in Scenarios 0 and 1 (P_WOff_0 and P_WOff_1, respectively), Sum of pollution swept off in Scenario 1 (P_Swept_1), Total number of sweeping events in Scenario 1 (Sw_Events), and the percent difference of pollution washed off between Secnario 0 and Scenario 1 (WOff_Diff). Two .csv files are outputted in the ArcGIS project folder titled "Scenario0_table.csv" and "Scenario1_table.csv". These tables show the pollution accumulation, pollution washoff, and pollution swept for each day in the simulation.


#### Additionally, a graph is outputted, titled "PASST_plot.png", which depicts the simulated pollution tracking, pollution swept, and pollution washoff for each road in the feature class. Please not that if more roads are added to the input feature class, the plot will likely have poor formatting. 


### Thank you for looking at my tool. Please feel free to reach out with any question or comments. 


