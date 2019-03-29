from gridrestore import Grid
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

scenarios = ['scenarioA','scenarioB','scenarioC','scenarioD']
sort_type = 'Cost_Person'
sort_order = 'Ascending'
restore_method = 'node'
sort_update = False

for scenario in scenarios:
	grid = Grid(scenario, budget=12.27, delay=7,debug=False, sort_type=sort_type, sort_order=sort_order, sort_update=sort_update, restore_method=restore_method)
	grid.restore_grid()
	savename = "Results_" + scenario + ".csv"
	grid.restore.to_csv(savename)