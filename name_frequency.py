#! /usr/bin/env python

#data from https://www.kaggle.com/kaggle/us-baby-names

import os
import sys
import sqlite3
import argparse
import pandas as pd
import matplotlib.pyplot as plt


# Plot style
pd.set_option('display.mpl_style', 'default') # Make the graphs a bit prettier
plt.rcParams['figure.figsize'] = (15, 5)


# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--names", nargs='+', help="Names to plot")
parser.add_argument("-y", "--year", type=int, help="Year of (name)")
parser.add_argument("-g", "--gender", choices=["M", "F", "B"], default="B", help="Gender of (names)")
parser.add_argument("-o", "--out", default="namePlot.png", help="Output figure name")
parser.add_argument("-m", "--normalize", action='store_true', help="Normalize name plot")
args = parser.parse_args()


# Read into dataframe from database
if not os.path.isfile('database.sqlite'):
    print " database.sqlite not in current directory. exiting..."
    sys.exit(0)

con = sqlite3.connect("database.sqlite")
df = pd.read_sql("SELECT * from NationalNames",con)
#df = pd.read_sql("SELECT * from StateNames",con)

## Read in data to dataframe from csv file
#df = pd.read_csv('NationalNames.csv')



def makeNamePlot( names, gender, year=-1 ):

    print "names =", names
    
    df_name = df[ df['Name'].isin(names) ]

    if gender=="B":
        df_name = df_name.groupby('Year', as_index=False).sum()

    else:
        df_name = df_name[ df_name['Gender']==gender ].groupby(['Year','Name'], as_index=False).sum()

        
    if args.normalize:
        print " normalizing the counts to peak value of 1"
        for name in names:
            maxVal = max(df_name[ df_name['Name']==name ]['Count'])
            nameReq = df_name['Name']==name
            df_name.loc[ nameReq, 'Count'] = df_name.loc[ nameReq, 'Count'] / maxVal


    if len(names) > 1:
        fig, ax = plt.subplots()
        labels = []
        for key, grp in df_name.groupby(['Name']):
            ax = grp.plot(ax=ax, kind='line', x='Year', y='Count')
            labels.append(key)
        lines, _ = ax.get_legend_handles_labels()
        ax.legend(lines, labels, loc='best')

    else :
        line, = plt.plot(df_name['Year'],df_name['Count'])
        
        if year > 0:
            my_count = df_name[ df_name['Year']==year ]['Count'].iloc[0]
            point, = plt.plot( [ year ], [ my_count ], 'or')

            plt.legend([line, point,], [names[0], year], numpoints=1)
        else:
            plt.legend([line], [names[0]]) 

    if args.normalize:
        plt.ylabel('Normalized Count')
    else:
        plt.ylabel('Count')
    plt.xlabel('Year')
    
    plt.savefig( args.out )



if args.names is not None:
    makeNamePlot( args.names, args.gender, args.year )
else:
    print "No names given"


