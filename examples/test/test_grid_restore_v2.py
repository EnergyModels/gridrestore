from gridrestore import Grid
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Actual Data
actual_x = 7.0 * np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30])
actual_y = np.array([0.0,0.0,0.092,0.17,0.216,0.262,0.379,0.432,0.43,0.466,0.656,0.684,0.614,0.654,0.698,0.57,0.604,0.635,0.6825,0.7018,0.7155,0.7677,0.8564,0.8743,0.8943,0.9179,0.934,0.9456,0.958,1.0,1.0])


scenario = 'scenarioA'
sort_types = ['Outage','Cost','Cost_Person']
sort_orders = ['Ascending','Descending']
restore_methods = ['node','component','hybrid']
sort_updates = [False, True]




df = pd.DataFrame()
f,a = plt.subplots(nrows=3,ncols=3)


# Rows
for i, restore_method in enumerate(restore_methods):
    # Columns
    for j, sort_type in enumerate(sort_types):

        # Access current subplot
        ax = a[i,j]
        title = "Sort by: " + sort_type + ", Restore by: " + restore_method
        # Plot actual data
        ax.plot(actual_x, actual_y, label='Actual', marker='o', linestyle='none', color='black')

        # Series
        for sort_order in sort_orders:
            for sort_update in sort_updates:

                savename = scenario +  '_' + restore_method + '_' + sort_type  + '_'+ sort_order  + '_'+ str(sort_update) + '_'
                grid = Grid(scenario, budget=12.27, delay=7,debug=False, sort_type=sort_type, sort_order=sort_order, sort_update=sort_update, restore_method=restore_method)
                grid.restore_grid()

                label = sort_order + '-' + str(sort_update)


                df[savename] = grid.restore.total_pwr_fr

                if sort_order=='Ascending':
                    color = 'red'
                elif sort_order=='Descending':
                    color = 'blue'

                if sort_update==True:
                    linestyle = '--'
                else:
                    linestyle = '-'

                ax.plot(grid.restore.time, grid.restore.total_pwr_fr, label=label,color=color,linestyle=linestyle)


        # Add legend, title and lables
        ax.legend(loc='lower right')
        ax.set_title(title)
        ax.set_xlabel('Timestep (-)')
        ax.set_ylabel('% with Power (-)')
