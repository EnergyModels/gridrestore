from gridrestore import Grid

grid = Grid('scenarioA', budget=10.8, debug=False, sort_type='Low', sort_update=False, restore_method='node')
priority = grid.prioritize()
print priority
# grid.restore_grid()
# grid.save_csv()