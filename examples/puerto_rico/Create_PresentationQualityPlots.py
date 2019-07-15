# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 17:19:50 2018

@author: jab6ft
"""
#=======================================================
# Imports
#=======================================================
# General
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
resolution = 1200 # DPI

# Actual Build-back
actual_x = 7.0 * np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30])
actual_y = 100.0 * np.array([0.0,0.0,0.092,0.17,0.216,0.262,0.379,0.432,0.43,0.466,0.656,0.684,0.614,0.654,0.698,0.57,0.604,0.635,0.6825,0.7018,0.7155,0.7677,0.8564,0.8743,0.8943,0.9179,0.934,0.9456,0.958,1.0,1.0])

# Series
files = ['Results_scenarioC.csv','Results_scenarioD.csv','Results_scenarioA.csv','Results_scenarioB.csv']
labels = ['Distributed - Natural Gas', 'Distributed - Hybrid', 'Centralized - Natural Gas','Centralized - Hybrid']
colors = [(.047, 0.149, 0.361),(0.847,0.000,0.067),(0.380,0.380,0.380),(0.957,0.451,0.125)] # Custom palette
linestyles = ['-','-','-','-']
markers = ['None','None','None','None',]

# Create plot
f = plt.figure()
# sns.set(style="white")
sns.set_style("white")
sns.set(context="talk")



for filename,label,color,linestyle,marker in zip(files,labels,colors,linestyles,markers):
    df = pd.read_csv(filename)
    x = df.loc[:,'time']
    y = 100.0 * df.loc[:,'total_pwr_fr']
    plt.plot(x,y,label=label,color=color,linestyle=linestyle,marker=marker)

plt.plot(actual_x,actual_y,label='Actual',color=(0.0,0.0,0.0),linestyle='None',marker='o')

# plt.legend(loc = 'upper center',bbox_to_anchor=(0.5, -0.1),ncol=len(labels)+1, scatterpoints = 1, frameon = False)
plt.legend(loc = 'upper center',bbox_to_anchor=(0.5, -0.2),ncol=3, scatterpoints = 1, numpoints=1,frameon = False)
plt.xlabel("Day (-)")
plt.ylabel("Population with electricity (%)")

f.set_size_inches([10,5])

# Save
savename = 'Results_GridRestoration_presentation.png'
plt.savefig(savename,dpi=resolution,bbox_inches="tight")