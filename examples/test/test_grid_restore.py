from gridrestore import Grid
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

scenario = 'scenarioA'
sort_types = ['Low','High','Cost','Cost_Person']
sort_updates = [False, True]
restore_methods = ['node','component']

df = pd.DataFrame()

for sort_type in sort_types:
    for sort_update in sort_updates:
        for restore_method in restore_methods:
            savename = scenario + ' - ' + sort_type + ' - ' +str(sort_update) + ' - ' +restore_method
            print savename
            grid = Grid(scenario, budget=10.8, debug=False, sort_type=sort_type, sort_update=sort_update, restore_method=restore_method)
            grid.restore_grid()

            df[savename] = grid.restore.total_pwr_fr
            if sort_type=='Low':
                color = 'red'
            elif sort_type=='High':
                color = 'blue'
            elif sort_type == 'Cost':
                color = 'green'
            else:
                color = 'purple'

            if sort_update==True:
                linestyle = '--'
            else:
                linestyle = '-'

            if restore_method=='node':
                marker = 'x'
            else:
                marker = 'o'
            plt.plot(grid.restore.time, grid.restore.total_pwr_fr, label=savename,color=color,linestyle=linestyle,marker=marker)


# Plot Actual Data
actual_x = 7.0 * np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30])
actual_y = np.array([0.0,0.0,0.092,0.17,0.216,0.262,0.379,0.432,0.43,0.466,0.656,0.684,0.614,0.654,0.698,0.57,0.604,0.635,0.6825,0.7018,0.7155,0.7677,0.8564,0.8743,0.8943,0.9179,0.934,0.9456,0.958,1.0,1.0])
plt.plot(actual_x,actual_y,label='Actual',marker='o',linestyle='none',color='black')

plt.legend()
plt.xlabel('Timestep (-)')
plt.ylabel('% with Power (-)')



