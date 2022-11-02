"""
This module creates two subplots showing the route of the JB trail Pike’s peak section. 

Author: Avery Jan
Date: 10-21-2021
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

# make up some data
x = np.linspace(-250.0, 150.0, 30)
y = np.linspace(-30.0, 30.0, 30)

# make up the trail coordinates
jb_trail_x = x + np.random.rand(len(y))*40-30
jb_trail_y = y

# make a grid that is a combination of every x and every y
X, Y = np.meshgrid(x, y)

# the park elevation at each coordinate pair (x,y)
Z = abs(150*np.cos(110*X)**2 + 300*np.sin(Y*12)) + 7000

# elevation along the JR trail
jb_trail_elevation = np.zeros(30)
j=0
for i in range(0,30):
    jb_trail_elevation[j] = Z[i,i]
    j+=1

# x-axis variable for second subplot representing distance along trail
jb_trail_transect = np.linspace(0,29,30)


fig = plt.figure(figsize=(12,6))


# create two subplots
fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=2)
fig.subplots_adjust(wspace=0.25)

# create contour plot
contour = ax1.contour(X, Y, Z, levels=4, cmap='inferno')

# create levels for labeling
ax1.clabel(contour, contour.levels, fontsize=4)

# set axes limits
ax1.set_xlim(-250, 150)
ax1.set_ylim(-30,30)

# set xticks and yticks
ax1.set_xticks([-250, -200, -150, -100, -50, 0, 50, 100, 150])
ax1.set_yticks([-30, -20, -10, 0, 10, 20, 30])

# format xticks and yticks label
ax1.tick_params(axis='x', color= 'grey', which = 'major', width =0, length=0, labelsize=6)
ax1.tick_params(axis='y', color = 'grey', which = 'major', width =0, length=0, labelsize=6.5)

# add JB trail
ax1.plot(jb_trail_x, jb_trail_y, label='JR Trail', linestyle='-.', linewidth=0.9, color ='k')

# set legend location
ax1.legend(loc="upper left", fontsize=5)

# add a grey background grid
ax1.grid(linestyle='-', linewidth=0.35, color='grey', zorder=-10)

# set spines color
plt.setp(ax1.spines.values(), linewidth=0.35, color='grey', zorder=-10)

# add a title
ax1.set_title("JB Trail Pup's Peak Section", fontsize=7)


# create filled plot
ax2.plot(jb_trail_transect, jb_trail_elevation, linestyle='-', linewidth=1, color='C2')

# create filled areas
ax2.fill_between(jb_trail_transect, jb_trail_elevation, np.zeros(len(x)), color='C2')

# set axes limits
ax2.set_xlim(0, 28.9)
ax2.set_ylim(7000, 8000)

# set xticks and yticks
ax2.set_xticks([0, 5, 10, 15, 20, 25])
ax2.set_yticks([7000, 7200, 7400, 7600, 7800, 8000])

# format xticks and yticks label
ax2.tick_params(axis='x', color= 'grey', which = 'major', width =0, length=0, labelsize=6.5)
ax2.tick_params(axis='y', color = 'grey', which = 'major', width =0, length=0, labelsize=6.5)

# add x and y labels
ax2.set_xlabel('Distance (mi)', fontsize=6)
ax2.set_ylabel('Elev. (ft)', fontsize=6)

# add a grey background grid
ax2.grid(linestyle='-', linewidth=0.35, color='grey', zorder=-10)

# annotate the filled plot
ax2.annotate('Pups Peak\nElevation 7,450 ft', xy = (10,7450), xytext=(11.5,7560), fontsize=6, arrowprops=dict(arrowstyle='simple', facecolor='k', edgecolor='none'))

# set spines color
plt.setp(ax2.spines.values(), linewidth=0.35, color='grey', zorder=-10)

# add a title
ax2.set_title("Trail Profile at Pup's Peak", fontsize=7)


# save the figure as a .png file
plt.savefig('Part1_figure.png', bbox_inches='tight')