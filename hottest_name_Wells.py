#! /usr/bin/env python

import os
import sys
import math
import pandas as pd
import time

start = time.time()
# Read in data to dataframe from csv file
df = pd.read_csv('NationalNames.csv')

# Focus only on recent times
df = df[ df['Year']>=2005 ]

# Determine rank for given year and gender
df['Rank'] = df.groupby(['Year', 'Gender'])['Count'].rank(ascending=False)

# Calculate the previous year's rank and count
df['PrevRank']   = df.groupby(['Name','Gender'])['Rank'].shift()
df['PrevCount']  = df.groupby(['Name','Gender'])['Count'].shift()
df['Prev2Count'] = df.groupby(['Name','Gender'])['PrevCount'].shift()
df['Prev3Count'] = df.groupby(['Name','Gender'])['Prev2Count'].shift()
df['Prev4Count'] = df.groupby(['Name','Gender'])['Prev3Count'].shift()

# Gives hotness value based on year and previous year value
def hotness( count, previousCount ):
    return math.sqrt(math.fabs(count-previousCount)) * (count-previousCount)/float(previousCount)

def predictCount(quality, countPrev):
    # Solve quality score equation for count in successive year. 
    count = countPrev + math.pow( math.fabs (quality * countPrev), 0.66667)  
    return count 

def calcPR(gender, numYears, hotPrev, hotPrev2, hotPrev3, count): 
    if numYears > 3 or numYears <= 0:
        print "Unsupported numYears = ", numYears
        sys.exit(0) 
    norm = 0
    PR = 0
    for n in range(numYears): 
        if n == 0:
            Q = hotPrev
        elif n == 1:
            Q = hotPrev2
        elif n == 2:
            Q = hotPrev3 
        norm += 1
        PR += Q 
    PR /= norm
    predict = predictCount(PR, count)
    if gender == "M" and predict < 220 or \
       gender == "F" and predict < 275:
        PR = 0         
    return PR            

# Determine hotness
df.loc[:,"Hotness"]      = df.apply(lambda row: hotness(row['Count'],     row['PrevCount']),  axis=1)
df.loc[:,"HotnessPrev"]  = df.apply(lambda row: hotness(row['PrevCount'], row['Prev2Count']), axis=1)
df.loc[:,"HotnessPrev2"] = df.apply(lambda row: hotness(row['Prev2Count'],row['Prev3Count']), axis=1)
df.loc[:,"HotnessPrev3"] = df.apply(lambda row: hotness(row['Prev3Count'],row['Prev4Count']), axis=1)
df.loc[:,"PR3"]          = df.apply(lambda row: calcPR(row['Gender'], 3, row['HotnessPrev'], row['HotnessPrev2'], row['HotnessPrev3'], row['Count']), axis=1) 
df.loc[:,"PR2"]          = df.apply(lambda row: calcPR(row['Gender'], 2, row['HotnessPrev'], row['HotnessPrev2'], row['HotnessPrev3'], row['Count']), axis=1) 
df.loc[:,"PR1"]          = df.apply(lambda row: calcPR(row['Gender'], 1, row['HotnessPrev'], row['HotnessPrev2'], row['HotnessPrev3'], row['Count']), axis=1) 

# Remove rows with missing data
df = df[ ~pd.isnull(df["Hotness"]) ]

# Require year or previous year be ranked in top 1000
df = df[ (df['Rank']<=1000) | (df['PrevRank']<=1000) ]

# Drop unnecessary column
df = df.drop('Id', 1)

totalScore3 = 0
totalScore2 = 0
totalScore1 = 0

# Print results for given year
def printResults( year ):
    global totalScore3, totalScore2, totalScore1 
    if not ( df["Year"] ).any():
        return
    use_df = df[ df["Year"]==year ]

    # sorted = use_df.sort(['Year','Hotness'],ascending=[0,0])
    sorted = use_df.sort(['Year','PR3'],ascending=[0,0])

    print
    print
    print "-------------------------- %d : TOP 10 RISERS -------------------------" % ( year )
    print
    print sorted[:10].reset_index(drop=True)
    scoreRiser3 = sorted[0:3]['Hotness'].sum()
    totalScore3 += scoreRiser3 
    sorted = use_df.sort(['Year','PR2'],ascending=[0,0])
    scoreRiser2 = sorted[0:3]['Hotness'].sum()  
    totalScore2 += scoreRiser2 
    sorted = use_df.sort(['Year','PR1'],ascending=[0,0])
    scoreRiser1 = sorted[0:3]['Hotness'].sum()    
    totalScore1 += scoreRiser1

    print "scoreRiser3 = ", scoreRiser3 
    print "scoreRiser2 = ", scoreRiser2
    print "scoreRiser1 = ", scoreRiser1 
    print
    print "-------------------------- %d : TOP 10 FALLERS -------------------------" % ( year )
    print
    print sorted[-10:].sort(['Year','Hotness'],ascending=[0,1]).reset_index(drop=True)
    print


years = set( df["Year"] )

for year in range(2010, 2015): 
    printResults( year )

print "TotalScore3 = ", totalScore3  
print "TotalScore2 = ", totalScore2  
print "TotalScore1 = ", totalScore1  

end = time.time()

print "Time elapsed = ", (end - start)  

