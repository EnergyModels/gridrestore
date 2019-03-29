#=============================================================================#
# Support Functions
# Written by Claire Trevisan and Jeff Bennett
#=============================================================================#

import numpy as np
import pandas as pd


# ================================#
# Internal functions
# ================================#
def or_fault(f_a, f_b):
    return f_a + f_b - f_a * f_b


def and_fault(f_a, f_b):
    return (f_a * f_b)


# ================================#
# Calculate fraction damaged
# ================================#

def damage_fraction(system, state):

    partial_restore = False



    if partial_restore ==True:
        state.loc[:, 'trans_fr'] = state.loc[:, 'trans_d'] / system.loc[:, 'Transmission_Towers']
        state.loc[:, 'sub_fr'] = state.loc[:, 'sub_d'] / system.loc[:, 'Substations']
        state.loc[:, 'dist_fr'] = state.loc[:, 'dist_d'] / system.loc[:, 'Distribution_Towers']
        state.loc[:, 'solar_fr'] = state.loc[:, 'solar_d'] / system.loc[:, 'Solar_Farms']
        state.loc[:, 'wind_fr'] = state.loc[:, 'wind_d'] / system.loc[:, 'Wind_Turbines']

    if partial_restore ==False:
        state.loc[:, 'trans_fr'] = np.ceil(state.loc[:, 'trans_d']) / system.loc[:, 'Transmission_Towers']
        state.loc[:, 'sub_fr'] = np.ceil(state.loc[:, 'sub_d']) / system.loc[:, 'Substations']
        state.loc[:, 'dist_fr'] = np.ceil(state.loc[:, 'dist_d']) / system.loc[:, 'Distribution_Towers']
        state.loc[:, 'solar_fr'] = np.ceil(state.loc[:, 'solar_d']) / system.loc[:, 'Solar_Farms']
        state.loc[:, 'wind_fr'] = np.ceil(state.loc[:, 'wind_d']) / system.loc[:, 'Wind_Turbines']

    trans_single_path = True

    if trans_single_path == True:
        ind = state.loc[:,'trans_fr']>0
        state.loc[ind, 'trans_fr'] = 1.0

    trans_regional_path = False
    if trans_regional_path == True:
        for region in system.loc[:, "Region"].unique():
            # Get centralized and distributed nodes for this region
            ind_d = (system.Region == region) & (system.Central != 'Y')
            if state.loc[ind_d,'trans_fr'].sum()>0:
                state.loc[ind_d, 'trans_fr'] = 1.0

    # Replace nan with 0
    state.loc[:, 'trans_fr'] = state.loc[:, 'trans_fr'].fillna(value=0.0)
    state.loc[:, 'sub_fr'] = state.loc[:, 'sub_fr'].fillna(value=0.0)
    state.loc[:, 'dist_fr'] = state.loc[:, 'dist_fr'].fillna(value=0.0)
    state.loc[:, 'solar_fr'] = state.loc[:, 'solar_fr'].fillna(value=0.0)
    state.loc[:, 'wind_fr'] = state.loc[:, 'wind_fr'].fillna(value=0.0)

    return state


# ================================#
# Calculate outage in each municipality
# ================================#
def outage(system, state, debug):

    # Extract relevant variables
        # System
    # system = self.system
    solar_cap = system.loc[:, 'Solar_MW']
    wind_cap = system.loc[:, 'Wind_MW']
    total_cap = system.loc[:, 'Total_MW']
        # State
    trans_f = state.loc[:, 'trans_fr']
    sub_f = state.loc[:, 'sub_fr']
    dist_f = state.loc[:, 'dist_fr']
    solar_f = state.loc[:, 'solar_fr']
    wind_f = state.loc[:, 'wind_fr']


    for region in system.loc[:,"Region"].unique():

        # Get centralized and distributed nodes for this region
        ind_c = (system.Region == region) & (system.Central == 'Y')
        ind_d = (system.Region == region) & (system.Central != 'Y')

        # ----------------
        # Power generation
        # ----------------
        # Calculate Centralized Power Outages
        central_solar_f_cap = sum(solar_f[ind_c] * solar_cap[ind_c])
        central_wind_f_cap = sum(wind_f[ind_c] * wind_cap[ind_c])
        central_total_cap = total_cap[ind_c].sum()

        if central_total_cap>0:
            central_pwr_f = (central_solar_f_cap + central_wind_f_cap) / central_total_cap
        else:
            central_pwr_f = 0.0
        # central_pwr_f = np.nan_to_num(central_pwr_f)  # Replace nan with 0's (may not have any centralized power gen)

        # Distributed
        dist_pwr_f = (solar_f[ind_d] * solar_cap[ind_d] + wind_f[ind_d] * wind_cap[ind_d]) / total_cap[ind_d]
        dist_pwr_f = np.nan_to_num(dist_pwr_f)  # Replace nan with 0's (may not have any distributed power gen)

        # Combined centralized & distributed
        power_f = or_fault(central_pwr_f, dist_pwr_f)

        # ----------------
        # Electric network
        # ----------------
        # Transmission or substation
        trans_sub_f = or_fault(trans_f[ind_d], sub_f[ind_d])
        # Transmission or substation or distribution
        network_f = or_fault(trans_sub_f, dist_f[ind_d])

        # ----------------
        # Combined
        # ----------------
        total_f = or_fault(network_f, power_f)
        # Store
        state.loc[ind_d, 'outage_fr'] = total_f
    state.loc[:, 'outage_pop'] = state.loc[:, 'outage_fr'] * system.loc[:, 'Population']
    state.loc[:, 'outage_pop'] = state.loc[:, 'outage_pop'].fillna(0.0)

    # ----------------
    # Calculate total outage
    # ----------------
    total_pop = system.loc[:, 'Population'].sum()
    pop_wo_pwr = state.loc[:,'outage_pop'].sum()
    total_outage_fr = pop_wo_pwr/total_pop

    if debug==True:
        print "total_outage_fr (%): " + str(round(total_outage_fr*100.0,2))

    return state, total_outage_fr

# ================================#
# Save timestep
# ================================#
def save_timestep(restore, system, t, costs, total_outage_fr):
    # Calculate total population
    tot_pop = system.loc[:, "Population"].sum()

    # Store variables of interest in Pandas Series
    cols = ['time', 'costs', 'total_outage_fr', 'total_pwr_fr', 'pop_wo_pwr', 'pop_w_pwr', ]
    t_n = pd.Series(index=cols)
    t_n['time'] = t
    t_n['costs'] = costs
    t_n['total_outage_fr'] = total_outage_fr
    t_n['total_pwr_fr'] = 1.0 - total_outage_fr
    t_n['pop_wo_pwr'] = (total_outage_fr) * tot_pop
    t_n['pop_w_pwr'] = (1.0 - total_outage_fr) * tot_pop

    # Append Series to DataFrame
    restore = restore.append(t_n, ignore_index=True)

    # Return updated Pandas Dataframe
    return restore