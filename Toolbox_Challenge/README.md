## Pollution Accumulation and Street Sweeping Tool (PASST)

### This ArcGIS toolbox tracks pollution accumulation, street sweeping events, and pollutant washoff due to rainfall across a series of roads. The tool requires two input files: roads feature class and land use feature class. An output dataset is created with all necessary information about the roads, pollutant accumulation, and street sweeping. Other user inputs include: 
#### -	road buffer distance (integer, units of feet)
#### -	Days in simulation (integer, units of days, between 1 and 365)
#### -	slope threshold (float, unitless, between 0.03 and 1)
#### -	buildup limit (integer, units of pounds)
#### -	days to reach buildup limit (integer, units of days, for each land use) * lower number means more rapid accumulation
#### -	street sweeper removal efficiency (float, units of percentage, between 0 and 1)

### To summarize the tool:
###3 1)	First the roads are buffered, given the user’s input buffer distance. The buffer is used to calculate the percentage of land use in the area around a road. Land uses of consideration are residential, forested, and commercial.
#### 2)	Based on the dominant land use of the road, the pollutant accumulation is tracked. Pollutant accumulation is based off a function of buildup limit and days to reach buildup limit, both of which are user inputs.
#### 3)	Rainfall is tracked using historical rain data from the Meteostat package (please note that Meteostat must be installed in your ArcGIS interpreter. Rain data from 2022 is preselected, which means the number of days in the simulation can only be between 1 and 365, which is a user input. On days when it rains more than 0.5 inches, 90% of accumulated pollution is washed off; on days when it rains more than 0.2 inches, only 20% of pollution is washed off. Washed off pollution is tracked.
#### 4)	Street sweeping events are set up to occur once the slope of the accumulation function decreases below a certain threshold (Slope Threshold in user inputs). The slope threshold is a percentage of the maximum buildup limit. Slope threshold must be between 0.03 and 1. Pollution removed from street sweeping and number of sweeping events are tracked.
#### 5)	The tool is formulated for two Scenarios: Scenario 0 has zero sweeping events and just tracks pollutant washoff due to rain; Scenario 1 includes street sweeping and pollutant washoff due to rain. The output roads dataset and messages appear to display these metrics comparing these two Scenarios.
#### 6)	Lastly a plot using matplotlib is generated for each of the roads in the dataset.
