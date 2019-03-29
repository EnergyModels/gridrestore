import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
from gridrestore import assess_damage, damage_fraction, outage, save_timestep

class Grid:

    def __init__(self, filename, budget=12.27, delay=7,debug=False, sort_type='Low', sort_order='Ascending',sort_update=False, restore_method='node'):

        self.filename = filename
        self.debug = debug
        self.sort_type = sort_type # 'Low' or 'High'
        self.sort_order = sort_order
        self.sort_update = sort_update # True, False
        self.restore_method = restore_method # 'component' or 'node'
        self.delay = delay # number of timesteps before restoration begins

        # ---------------------------------------
        # Repair cost and budget
        # ---------------------------------------
        cost = {}
        cost['budget'] = budget*1E6 # Million dollars
        cost['trans'] = 0.4E6  # cost to repair transmission structure(Ouyang et al 2014)
        cost['dist'] = 2500.0  # cost to repair one distribution pole (Ouyang et al 2014)
        cost['sub'] = 5.5E6  # cost to repair one substation (moderate) (Ouyang et al 2014)
        cost['solar'] = 850.0  # source: http://energyinformative.org/solar-panels-installation-time
        cost['wind'] = 1750000.0
        # Store
        self.cost = cost

        # ---------------------------------------
        # Import data and extract variables
        #---------------------------------------
        df = pd.read_csv(filename + '.csv')

        cols = ['Municipality','Population',  # County
                'Windspeed_mph','Windspeed_ms','Windspeed_kmph','Windspeed_knots',  # Hurricane
                'Transmission_Towers','Substations','Distribution_Towers','Solar_Farms','Wind_Turbines',  # Infrastructure
                'Solar_MW','Wind_MW','Total_MW']  # Electric capacity
        system = pd.DataFrame(columns=cols)

        # General
        system.loc[:, 'Node'] = df.loc[:, "Node"]  # Name
        system.loc[:, 'Central'] = df.loc[:, "Central"]  # Y or N
        system.loc[:, 'Region'] = df.loc[:, "Region"]  # Name
        system.loc[:, 'Population'] = df.loc[:, "Population"]

        # Hurricane peak windspeed
        system.loc[:, 'Windspeed_mph'] =  df.loc[:, "Windspeed_mph"]

        # Infrastructure
        system.loc[:, 'Transmission_Towers']= df.loc[:, "Transmission_towers"]
        system.loc[:, 'Substations'] = df.loc[:, "Substations"]
        system.loc[:, 'Distribution_Towers'] = df.loc[:, "Distribution_towers"]
        system.loc[:, 'Solar_Farms'] = df.loc[:, "Solar_farms"]
        system.loc[:, 'Wind_Turbines'] = df.loc[:, "Wind_turbines"]

        # Electric grid capacity
        system.loc[:, 'Solar_MW'] = df.loc[:, "Solar_MW"]
        system.loc[:, 'Wind_MW'] = df.loc[:, "Wind_MW"]
        system.loc[:, 'Total_MW'] = df.loc[:, "Total_MW"]

        # Variations of Windspeed
        system.loc[:, 'Windspeed_ms'] = system.loc[:, 'Windspeed_mph'] * 0.44704
        system.loc[:, 'Windspeed_kmph'] = system.loc[:, 'Windspeed_mph'] * 1.60934
        system.loc[:, 'Windspeed_knots'] = system.loc[:, 'Windspeed_mph'] / 1.15078

        # Store Dataframe
        self.system = system

        # ---------------------------------------
        # State of electric grid after hurricane
        # ---------------------------------------

        cols = ['municipality', 'outage_fr', 'outage_pop',
                'trans_d', 'sub_d', 'dist_d', 'solar_d', 'wind_d', # Number damaged
                'trans_fr', 'sub_fr', 'dist_fr', 'solar_fr', 'wind_fr']  # Damage fraction
        init_state = pd.DataFrame(columns=cols)

        # General
        init_state.loc[:, 'municipality'] = system.loc[:, 'Municipality']

        # Number damaged
        init_state = assess_damage(system, init_state)

        # Damage fraction and initial outage
        init_state = damage_fraction(self.system, init_state)
        init_state, self.total_outage_fr = outage(self.system, init_state, self.debug)

        # Store
        self.init_state = init_state

        # Create copy of init_state to update during restoration
        state = copy.deepcopy(init_state)
        self.state = state

        # ---------------------------------------
        # Analyze Repair
        # ---------------------------------------
        # Total Repair cost
        self.repair_cost = state.loc[:, 'trans_d'] * cost['trans'] + state.loc[:, 'sub_d'] * cost['sub'] \
                           + state.loc[:, 'dist_d'] * cost['dist'] + state.loc[:, 'solar_d'] * cost['solar'] \
                           + state.loc[:, 'wind_d'] * cost['wind']

        self.total_cost = sum(self.repair_cost) / 1E6  # Million (M$)
        self.repair_time = self.total_cost * 1E6 / cost['budget'] # Days

        # ---------------------------------------
        # Prepare Dataframe to store grid restoration
        # ---------------------------------------
        cols = ['time', 'costs','total_outage_fr', 'total_pwr_fr', 'pop_wo_pwr', 'pop_w_pwr',]
        self.restore = pd.DataFrame(columns=cols)
        self.restore = save_timestep(self.restore, self.system, 0, 0, self.total_outage_fr)

    # ================================#
    # Determine repair priority
    # ================================#
    def prioritize(self):





        # to_sort = pd.concat(self.system, self.state)

        # to_sort = pd.concat([self.system, self.state], axis=1)


        # Sort type - Outage, Cost, or Cost/Person
        if self.sort_type =='Outage':
            sorted = self.repair_cost.sort_values()

        elif self.sort_type =='Cost':
            sorted = self.repair_cost.sort_values()

        elif self.sort_type =='Cost_Person':
            cost_person = self.repair_cost / self.system.loc[:,"Population"]
            sorted = cost_person.sort_values()


        # Ascending vs. Descending
        if self.sort_order == 'Ascending':
            sorted = sorted
        elif self.sort_order == 'Descending':
            sorted = sorted[::-1]

        priority = sorted.index

        # # Prioritize based on
        # if self.sort_type == 'Low': # 'Low' Outage
        #     # outage_pop = self.state.outage_pop.fillna(0.0) # Prioritize centralized plants over distributed
        #     # priority = np.argsort(outage_pop)
        #     # priority = np.argsort(outage_pop)
        #
        #     sorted = to_sort.sort_values(by=['outage_pop','Windspeed_mph'],ascending=True)
        #
        #
        #
        #
        #
        # # else: # 'High' Outage
        # elif self.sort_type == 'High':
        #     sorted = to_sort.sort_values(by=['outage_pop', 'Windspeed_mph'], ascending=False)
        #     # outage_pop = self.state.outage_pop.fillna(1E9) # Prioritize centralized plants over distributed
        #     # priority = np.argsort(outage_pop)[::-1]
        #
        #
        # elif self.sort_type =='Cost':
        #     sorted = self.repair_cost.sort_values()
        #
        # elif self.sort_type =='Cost_Person':
        #     cost_person = self.repair_cost / self.system.loc[:,"Population"]
        #     sorted = cost_person.sort_values()




        # ind_c = (self.system.Central == 'Y')
        # priority = np.append(ind_c, priority)

        return priority

    # ================================#
    # Plot restoration
    # ================================#
    def plot(self):
        plt.plot(self.restore.t, self.restore.t)
        plt.xlabel('Timesteps (-)')
        plt.ylabel('% With Power')

    # ================================#
    # Save restoration to CSV
    # ================================#
    def save_csv(self, savename):
        self.restore.to_csv(savename + '.csv')

    # ================================#
    # Restore electric grid
    # ================================#
    def restore_grid(self):

        priority = self.prioritize()

        t = 0
        while self.total_outage_fr > 0.001:

            t = t + 1

            if t<=self.delay:
                costs = 0.0
            else:
                # Single time step
                costs = self.timestep(priority)

                # Update damage fraction and outage
                self.state = damage_fraction(self.system, self.state)
                self.state, self.total_outage_fr = outage(self.system, self.state, self.debug)

            # Save results
            self.restore = save_timestep(self.restore, self.system, t, costs, self.total_outage_fr)

            # Update sort priority
            if self.sort_update==True:
                priority = self.prioritize()

    # ================================#
    # Repair single component in a given timestep
    # ================================#
    def repair_component(self, index, state_var, cost_var, costs):

        if costs < self.cost['budget'] and self.state.loc[index, state_var] > 0:
            repairable = (self.cost['budget'] - costs) / self.cost[cost_var]

            if repairable < self.state.loc[index, state_var]:
                self.state.loc[index, state_var] = self.state.loc[index, state_var] - repairable
                repaired = repairable
            else:
                repaired = self.state.loc[index, state_var]
                self.state.loc[index, state_var] = 0.0

            costs = costs + repaired * self.cost[cost_var]

        return costs


    # ================================#
    # Single timestep
    # ================================#
    def timestep(self, priority):

        costs = 0.0

        # --------------------------- #
        # Component Method
        # --------------------------- #
        if self.restore_method == 'component':

            # Transmission
            if costs < self.cost['budget']:
                for index in priority:
                    state_var = 'trans_d'
                    cost_var = 'trans'
                    costs = self.repair_component(index, state_var, cost_var, costs)

            # Substation
            if costs < self.cost['budget']:
                for index in priority:
                    state_var = 'sub_d'
                    cost_var = 'sub'
                    costs = self.repair_component(index, state_var, cost_var, costs)

            # Distribution
            if costs < self.cost['budget']:
                for index in priority:
                    state_var = 'dist_d'
                    cost_var = 'dist'
                    costs = self.repair_component(index, state_var, cost_var, costs)

            # Solar Energy
            if costs < self.cost['budget']:
                for index in priority:
                    state_var = 'solar_d'
                    cost_var = 'solar'
                    costs = self.repair_component(index, state_var, cost_var, costs)

            # Wind Energy
            if costs < self.cost['budget']:
                for index in priority:
                    state_var = 'wind_d'
                    cost_var = 'wind'
                    costs = self.repair_component(index, state_var, cost_var, costs)

        # --------------------------- #
        # Node Method
        # --------------------------- #
        elif self.restore_method == 'node':

            for index in priority:

                # Transmission
                if costs < self.cost['budget']:
                    state_var = 'trans_d'
                    cost_var = 'trans'
                    costs = self.repair_component(index, state_var, cost_var, costs)

                # Substation
                if costs < self.cost['budget']:
                    state_var = 'sub_d'
                    cost_var = 'sub'
                    costs = self.repair_component(index, state_var, cost_var, costs)

                # Distribution
                if costs < self.cost['budget']:
                    state_var = 'dist_d'
                    cost_var = 'dist'
                    costs = self.repair_component(index, state_var, cost_var, costs)

                # Solar Energy
                if costs < self.cost['budget']:
                    state_var = 'solar_d'
                    cost_var = 'solar'
                    costs = self.repair_component(index, state_var, cost_var, costs)

                # Wind Energy
                if costs < self.cost['budget']:
                    state_var = 'wind_d'
                    cost_var = 'wind'
                    costs = self.repair_component(index, state_var, cost_var, costs)

        # --------------------------- #
        # Hybrid Method
        # --------------------------- #
        elif self.restore_method == 'hybrid':

            for index in priority:

                # Transmission
                if costs < self.cost['budget']:
                    state_var = 'trans_d'
                    cost_var = 'trans'
                    costs = self.repair_component(index, state_var, cost_var, costs)

                # Substation
                if costs < self.cost['budget']:
                    state_var = 'sub_d'
                    cost_var = 'sub'
                    costs = self.repair_component(index, state_var, cost_var, costs)

                # Distribution
                if costs < self.cost['budget']:
                    state_var = 'dist_d'
                    cost_var = 'dist'
                    costs = self.repair_component(index, state_var, cost_var, costs)

            for index in priority:

                # Solar Energy
                if costs < self.cost['budget']:
                    state_var = 'solar_d'
                    cost_var = 'solar'
                    costs = self.repair_component(index, state_var, cost_var, costs)

                # Wind Energy
                if costs < self.cost['budget']:
                    state_var = 'wind_d'
                    cost_var = 'wind'
                    costs = self.repair_component(index, state_var, cost_var, costs)

        return costs