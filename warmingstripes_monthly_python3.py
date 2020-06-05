#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 13:03:43 2020

@author: Scientists4Future Leipzig
"""

import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import urllib
from matplotlib.colors import LinearSegmentedColormap

## Manual entries required:
# Enter number of month to plot - add '0' before months with one digit
month = "04"
# Enter your local path and filename where to save the raw data
local ="regional_averages_tm_"+month+".txt"

## Definition of manual colormap:
def make_cmap(colors, position=None, bit=False):
    '''
    make_cmap takes a list of tuples which contain RGB values. The RGB
    values may either be in 8-bit [0 to 255] (in which bit must be set to
    True when called) or arithmetic [0 to 1] (default). make_cmap returns
    a cmap with equally spaced colors.
    Arrange your tuples so that the first color is the lowest value for the
    colorbar and the last is the highest.
    position contains values from 0 to 1 to dictate the location of each color.
    http://schubert.atmos.colostate.edu/~cslocum/custom_cmap.html
    '''
    bit_rgb = np.linspace(0,1,256)
    if position == None:
        position = np.linspace(0,1,len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")
    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])
    cdict = {'red':[], 'green':[], 'blue':[]}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)
    return cmap
#Colors to match best to color bar of original warming stripes:
colors = [(8, 48, 107),
(8, 81, 156),
(33, 113, 181),
(66, 146, 198),
(107, 174, 214),
(158, 202, 225),
(198, 219, 239),
(222, 235, 247),
(254, 224, 210),
(252, 187, 161),
(252, 146, 114),
(251, 106, 74),
(239, 59, 44),
(203, 24, 29),
(165, 15, 21),
(103, 0, 13)]
### Call the function make_cmap which returns your colormap
my_cmap = make_cmap(colors, bit=True)

### RETRIEVE DATA FROM DWD
#link to DWD server
link = "https://opendata.dwd.de/climate_environment/CDC/regional_averages_DE/monthly/air_temperature_mean/regional_averages_tm_"+month+".txt"
#retrieve data and cleanup !for Python2.7 comment out lines 39, 40 and uncomment lines 41, 42
tm = urllib.request.urlretrieve(link, local)
urllib.request.urlcleanup()
#tm = urllib.urlretrieve(link, local)
#urllib.urlcleanup()
#read in the data as pandas table
data = pd.read_table(tm[0],skiprows=1, sep=';')


#### SOME SPECIFICATIONS BEFORE PLOTTING
# reference period for mean calculation 1971 - 2000 according to warming stripes by Ed Hawkins (see https://showyourstripes.info/faq)
ref_min = 1971
ref_max = 2000

#select the data during the refence period
ref_data = data[(data['Jahr']>=ref_min) & (data['Jahr']<=ref_max)]

#reference period for the standard deviation, according to the original stripes
ref_min_std = 1901
ref_max_std = 2000

#select the data during the std ref period
ref_data_std = data[(data['Jahr']>=ref_min_std) & (data['Jahr']<=ref_max_std)]

# just a dictionary for the quick selecetion of a federal state by number
regio = {1:'Sachsen',2:'Deutschland',3:'Brandenburg/Berlin', 4:'Brandenburg',
       5:'Baden-Wuerttemberg', 6:'Bayern', 7:'Hessen', 8:'Mecklenburg-Vorpommern',
       9:'Niedersachsen', 10:'Niedersachsen/Hamburg/Bremen',
       11:'Nordrhein-Westfalen', 12:'Rheinland-Pfalz', 13:'Schleswig-Holstein',
       14:'Saarland', 15:'Sachsen-Anhalt',
       16:'Thueringen/Sachsen-Anhalt', 17:'Thueringen'}

### PLOTTING OF DROUGHTSTRIPES
#select the federal state you want to plot, numbers according to dictionary above, here: Sachsen, Deutschland
regio_lst=[1,2]
#loop through selected states and create a plot for each
for reg in regio_lst:
    region = regio[reg]
    # calculate the standard deviation for the period definded above
    std = ref_data_std[region].std()
    #select temperature in the region
    temps_region = data[region]

    # calculate the temperature anomaly i.e. deviation from defined mean of ref period
    temps = temps_region - ref_data[region].mean()
    ## stack data to be able to plot them with imshow
    stacked_temps = np.stack((temps, temps))

    #min and max values for the colormap according to the original stripes
    vmin = -2.6*std
    vmax = 2.6*std

    ## plotting
    fig = plt.figure(figsize=(16,9))#adjust figsize, for example for cubic figure
    #plot the image, with manual color bar defined above in make_cmap function
    img = plt.imshow(stacked_temps, cmap=my_cmap, interpolation='none', aspect='auto', vmin=vmin, vmax=vmax)
    #this just turns all labels, axis etc off so that there are only the stripes
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    #save in your current directory
    plt.savefig("warmingstripes_"+temps.name+'_'+month+'_'+str(data['Jahr'].min())+'-'+str(data['Jahr'].max())+".jpg", bbox_inches = 'tight', pad_inches = 0, dpi=400)
