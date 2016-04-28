#! /usr/bin/env python

import os
import sys
import math
import pandas as pd

# Read in data to dataframe from csv file
df = pd.read_csv('NationalNames.csv')

# Focus only on recent times
df = df[ df['Year']>=2010 ]

# Determine rank for given year and gender
df['Rank'] = df.groupby(['Year', 'Gender'])['Count'].rank(ascending=False)

# Calculate the previous year's rank and count
df['PrevRank'] = df.groupby(['Name','Gender'])['Rank'].shift()
df['PrevCount'] = df.groupby(['Name','Gender'])['Count'].shift()

# Gives hotness value based on year and previous year value
def hotness( count, previousCount ):
    return math.sqrt(math.fabs(count-previousCount)) * (count-previousCount)/float(previousCount)

# Determine hotness
df.loc[:,"Hotness"] = df.apply(lambda row: hotness(row['Count'],row['PrevCount']), axis=1)

# Remove rows with missing data
df = df[ ~pd.isnull(df["Hotness"]) ]

# Require year or previous year be ranked in top 1000
df = df[ (df['Rank']<=1000) | (df['PrevRank']<=1000) ]

# Drop unnecessary column
df = df.drop('Id', 1)

# Print results for given year
def printResults( year ):
    if not ( df["Year"] ).any():
        return
    use_df = df[ df["Year"]==year ]

    sorted = use_df.sort(['Year','Hotness'],ascending=[0,0])

    print
    print
    print "-------------------------- %d : TOP 10 RISERS -------------------------" % ( year )
    print
    print sorted[:10].reset_index(drop=True)
    print
    print "-------------------------- %d : TOP 10 FALLERS -------------------------" % ( year )
    print
    print sorted[-10:].sort(['Year','Hotness'],ascending=[0,1]).reset_index(drop=True)
    print


years = set( df["Year"] )

for year in years:
    printResults( year )
