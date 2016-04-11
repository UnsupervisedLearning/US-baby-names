#! /usr/bin/env python

#data from https://www.kaggle.com/kaggle/us-baby-names

# example usage:
# bokeh serve --show example_bokeh.py

import os
import sys
import sqlite3
import argparse
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.plotting import Figure
from bokeh.palettes import Spectral11
from bokeh.models import ColumnDataSource, HoverTool, HBox, VBoxForm
from bokeh.models.widgets import Slider, Select, TextInput, RadioGroup
from bokeh.io import curdoc
#from bokeh.sampledata.movies_data import movie_path


## Read in data to dataframe from csv file
names = pd.read_csv('NationalNames.csv')


# Create input controls
gender = Select(title="Gender", value="M", options=['M','F'])
radio_group = RadioGroup(labels=["M", "F"], active=0)
name_of_interest = TextInput(title="Name")

# Palette of colors to use for later
mypalette=Spectral11[0:10]

# Define what data is displayed when hovering over graph
hover = HoverTool(tooltips=[
    ("Name","@name"),
    ("Year", "@year"),
    ("Count", "@count"),
    ("Gender", "@gender")
])

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], name=[], year=[], count=[], gender=[]))

# Setup plot
plot = Figure(plot_height=600, plot_width=800, title="", toolbar_location=None, tools=[hover])
plot.line('x', 'y', source=source, line_width=3, line_color='blue', line_alpha=0.6)

# Determine what data should be plotted
def select_names():
    default_name = "Howard"
    gender_val = gender.value
    name_val = name_of_interest.value.strip()
    name_list = []
    if ',' in name_val:
        name_list = name_val.split(",")
        name_list = [ i.strip() for i in name_list ]
    else :
        name_list.append( name_val )

    selected = names[ names['Gender']==gender_val ]
    if name_val != "" :
        test_name = selected['Name'].isin(name_list)
        if sum(test_name) < 1 :
            selected = selected[ selected['Name']==default_name ]
        else :
            selected = selected[ selected['Name'].isin(name_list) ]
    else :
        # Default name to prevent always plotting all data
        selected = selected[ selected['Name']==default_name ]
        
    return selected

def update(attrname, old, new):
    df = select_names()
    x_name = "Year"
    y_name = "Count"

    plot.xaxis.axis_label = x_name
    plot.yaxis.axis_label = y_name
    #plot.title = "%d movies selected" % len(df)
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        name=df["Name"],
        year=df["Year"],
        count=df["Count"],
        gender=df["Gender"],
    )


# Define which controls (defined above) will be included
controls = [gender, name_of_interest]
for control in controls:
    control.on_change('value', update)


inputs = HBox(VBoxForm(*controls), width=300)

update(None, None, None) # initial load of the data

curdoc().add_root(HBox(inputs, plot, width=1100))
