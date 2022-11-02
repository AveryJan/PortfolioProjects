"""
This module creates three subplots showing the results from a material science experiment (stress and strain). 

Author: Avery Jan
Date: 10-22-2021
"""

from matplotlib import pyplot as plt
import numpy as np
import matplotlib
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

stress_strain = np.loadtxt('stress_strain.csv', delimiter=',')

#plate failure project
time = np.linspace(0,100, 101)
displacement = np.concatenate([np.random.rand(70), np.random.rand(31)+3])
x = np.linspace(-10.0, 10.0, 1000)
y = np.linspace(-10.0, 10.0, 1000)

ave_displacement = moving_average(displacement, n=4)
ave_displacement = np.concatenate([ave_displacement[0:3], ave_displacement])

stress_true = stress_strain[:,0]
strain_true = stress_strain[:,1]
stress_est = stress_strain[:,2]
strain_est = stress_strain[:,3]
stress_est_max = 1.15*stress_est
stress_est_min = .9*stress_est

# grid for cross section
X, Y = np.meshgrid(x, y)
Z = abs(X + Y)

# create a figure object
fig = plt.figure(figsize=(12,8))

# create subplots
gspec= fig.add_gridspec(ncols=4, nrows=2)
ax1 = fig.add_subplot(gspec[0,:4])
ax2 = fig.add_subplot(gspec[1,:2])
ax3 = fig.add_subplot(gspec[1,2:])
fig.subplots_adjust(hspace=.5, wspace=0.25)


# 1. create a scatter plot and a line plot on ax1
ax1.scatter(time, displacement, label='Observation', c='red', edgecolor=None, alpha=0.8, cmap='summer', s=25)
ax1.plot(time, ave_displacement, label='Rolling Mean', c='C0', linestyle='--', linewidth = 1.5, alpha=1.0)

# set axes limits
ax1.set_xlim(0, 100)
ax1.set_ylim(-.2, 4.2)


# set xticks and yticks
ax1.set_xticks([0, 20, 40, 60, 80, 100])
ax1.set_yticks([0, 1, 2, 3, 4])

# format xticks and yticks label
ax1.tick_params(axis='x', color='grey', which = 'major', width =1.0, length=7, labelsize=10)
ax1.tick_params(axis='y', color='grey', which = 'major', width =1.0, length=7, labelsize=10)

# annotate the line plot
ax1.annotate('Fracture occured\nafter 65 seconds', xy = (70,2), xytext=(50,2.7), arrowprops=dict(arrowstyle='simple', facecolor='k', edgecolor='none'))


# add x and y labels
ax1.set_xlabel('Time (s)', fontsize=10)
ax1.set_ylabel('Displacement ($µm$)', fontsize=10)

# add a title
ax1.set_title('Plate Fracture Test Results', fontsize=12)

# set legend location
ax1.legend(loc="upper left")


# 2. create true and estimated line plots on ax2
ax2.plot(strain_true, stress_true, label ='Actual', c='green', linestyle='-', linewidth = 1.0, alpha=1.0)
ax2.plot(strain_est, stress_est , label='Estimated', c='green', linestyle='--', linewidth = 1.0, alpha=1.0)

# create 95% confidence interval filled plot
ax2.plot(strain_est, stress_est_max, c='green', linestyle='None')
ax2.plot(strain_est, stress_est_min, c='green', linestyle='None')
ax2.fill_between(strain_est, stress_est_max, stress_est_min, label='95% conf', color = 'green', alpha =0.15)

# set axes limits
ax2.set_xlim(0, 0.10)
ax2.set_ylim(-20, 580)

# set xticks and yticks
ax2.set_xticks([0.00, 0.02, 0.04, 0.06, 0.08, 0.10])
ax2.set_yticks([0, 100, 200, 300, 400, 500])

# format xticks and yticks label
ax2.tick_params(axis='x', color='grey', which = 'major', width =1.0, length=3, labelsize=16)
ax2.tick_params(axis='y', color='grey', which = 'major', width =1.0, length=3, labelsize=16)

# add x and y labels
ax2.set_xlabel('$ε(kN/cm^2)$', fontsize=10)
ax2.set_ylabel('$σ$ (kN)', fontsize=10)

# add a title
ax2.set_title('Stress Strain Relationship', fontsize=12)

# set legend location
ax2.legend(loc="lower right")


# 3. create an imshow colorplot on ax3
# create the heatmap
im=ax3.imshow(Z, cmap='inferno')

# set x axis and y axis limits
ax3.set_xlim(0,1000)
ax3.set_ylim(1000,0)

# set xticks and yticks
ax3.set_xticks([0, 200, 400, 600, 800])
ax3.set_yticks([0, 200, 400, 600, 800])

# format xticks and yticks label
ax2.tick_params(axis='x', color='grey', which = 'major', width =1.0, length=7, labelsize=6)
ax2.tick_params(axis='y', color='grey', which = 'major', width =1.0, length=7, labelsize=6.5)

# add x and y labels
ax3.set_xlabel('x (cm)', fontsize=10)
ax3.set_ylabel('y (cm)', fontsize=10)

# Add a title
ax3.set_title('Plate Cross section', fontsize=10)

# create colorbar
divider = make_axes_locatable(ax3)
cax = divider.append_axes('right', size='5%', pad=0.1)
cbar = fig.colorbar(im, cax=cax, label='$σ$(kN)')


# save the figure as a .png file 
plt.savefig('Part2_figure.png', bbox_inches='tight')