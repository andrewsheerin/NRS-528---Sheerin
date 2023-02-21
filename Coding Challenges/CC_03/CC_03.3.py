# 3. Working with CSV
# Using the Atmospheric Carbon Dioxide Dry Air Mole Fractions from quasi-continuous daily measurements at
# Mauna Loa, Hawaii dataset, obtained from here (https://github.com/datasets/co2-ppm-daily/tree/master/data).
#
# Using Python (csv) calculate the following:
#
# 1. Annual average for each year in the dataset.
# 2. Minimum, maximum and average for the entire dataset.
# 3. Seasonal average if Spring (March, April, May), Summer (June, July, August), Autumn (September, October, November)
# and Winter (December, January, February).
# 4. Calculate the anomaly for each value in the dataset relative to the mean for the entire time series.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# I feel more comfortable working with Pandas
df = pd.read_csv('co2-ppm-daily.csv', usecols=['date', 'value'])

##### TASK 1

# Create lists for the years
all_years = []
unique_years = []
for i in range(len(df)):
    year = df['date'][i].split('-')[0]
    all_years.append(year)
    if year not in unique_years:
        unique_years.append(year)

df['year'] = all_years

# Calculate annual averages and print
annual_avg_list = []
for year in unique_years:
    annual_sum = 0.0
    annual_count = 0
    annual_avg = 0.0
    for i in range(len(df)):
        y = int(df['date'][i].split('-')[0])
        if y == int(year):
            annual_sum += df['value'][i]
            annual_count += 1

    annual_avg = annual_sum / float(annual_count)
    annual_avg_list.append(annual_avg)
    print(str(year) + ': ' + str(annual_avg))

#### TASK 2

# MAXIMUM
maximum = max(df['value'])
print('Maximum CO2 value: ' + str(maximum))

# MINIMUM
minimum = min(df['value'])
print('Minimum CO2 value: ' + str(minimum))

# AVERAGE
mean = sum(df['value']) / len(df['value'])
print('Average CO2 value: ' + str(mean))

#### TASK 3

# First, create lists for all the months
all_months = []
unique_months = []
for i in range(len(df)):
    month = df['date'][i].split('-')[1]
    all_months.append(month)
    if month not in unique_months:
        unique_months.append(month)

df['month'] = all_months

# Print unique months to know the order they appear in the list, need this for seasonal average calculation
print(unique_months)

# Calculate averages for each month
month_avg_list = []
for month in unique_months:
    month_sum = 0.0
    month_count = 0
    month_avg = 0.0
    for i in range(len(df)):
        m = int(df['date'][i].split('-')[1])
        if m == int(month):
            month_sum += df['value'][i]
            month_count += 1

    month_avg = month_sum / float(month_count)
    month_avg_list.append(month_avg)
    print(str(month) + ': ' + str(month_avg))

# Average the monthly averages for each season and print, note the order obtained from unique_months list
winter_avg = (month_avg_list[7] + month_avg_list[8] + month_avg_list[9])/3
spring_avg = (month_avg_list[0] + month_avg_list[1] + month_avg_list[2])/3
summer_avg = (month_avg_list[10] + month_avg_list[3] + month_avg_list[4])/3
fall_avg = (month_avg_list[5] + month_avg_list[11] + month_avg_list[6])/3
print('winter average: ' + str(winter_avg))
print('spring average: ' + str(spring_avg))
print('summer average: ' + str(summer_avg))
print('fall average: ' + str(fall_avg))

#### TASK 4

## I tried a few statistics tests for this part. It's been a while since I've tried this stuff
## and wanted to see if I could do it in python

# Calculates difference from the mean, aka anomaly
anomalies = []
for i in range(len(df)):
    anomaly = df['value'][i] - mean
    anomalies.append(anomaly)

df['anomaly'] = anomalies

# Calculates z-score for each value (how many standard deviations the value is from the mean)
z_scores = []
for i in range(len(df)):
    z_score = np.abs((df['value'][i] - mean) / np.std(df['value']))
    z_scores.append(z_score)

df['z_score'] = z_scores

# Determines outliers, if z-score is greater than 1.96, aka outside the 95% confidence interval
# Outlier = 1 if outlier, 0 if not
outlier =[]
outlier_count = 0
for i in range(len(df)):
    if df['z_score'][i] > 1.96:
        bin = 1
        outlier.append(bin)
        outlier_count += 1
    else:
        bin = 0
        outlier.append(bin)

df['outlier'] = outlier
print('Outlier count: ' + str(outlier_count))

print(df)