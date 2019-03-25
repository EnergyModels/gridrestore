#=============================================================================#
# Support Functions
# Written by Claire Trevisan and Jeff Bennett
#=============================================================================#

import numpy as np

#calculates the percent of failure of each infrastructure type in a municipality
def percent_failed(failed, total): 
    percent = []
    for i in range(len(total)):
        if total[i] <= 0.0:
            percent.append(0.0)
        else:
            if failed[i]<0.0:
                percent.append(0.0)
            else:
                percent.append(failed[i]/total[i])
    return percent

#calculates the % outage in a municipality
def outage_municip(n_central, trans_f, sub_f, dist_f, solar_f, wind_f, solar_cap, wind_cap, total_cap): #calculates the % outage in a municipality
    
    failure_rate = []

    # Calculate Centralized Power Outages
    central_solar_f = 0.0
    central_wind_f = 0.0
    central_total_f = 0.0
    for i in range(n_central):
        central_solar_f_cap = central_solar_f + solar_f[i]*solar_cap[i]
        central_wind_f_cap = central_wind_f + wind_f[i]*wind_cap[i]
        central_total_cap = central_total_f + total_cap[i]
        failure_rate.append(0.0)
    if central_total_cap > 0:
        central_pwr_f = (central_solar_f_cap + central_wind_f_cap)/central_total_cap
    else:
        central_pwr_f = 0.0
        
    # Iterate through each municipality
    for i in np.arange(n_central,len(dist_f)):
#        failure = (sub_f[i]+trans_f[i]-sub_f[i]*trans_f[i])+dist_f[i]-(sub_f[i]+trans_f[i]-sub_f[i]*trans_f[i])*dist_f[i]
        
        # Transmission or substation
        trans_sub_f = or_fault(trans_f[i], sub_f[i])
        # Transmission or substation or distribution
        network_f = or_fault(trans_sub_f, dist_f[i])
        # Power generation
        if total_cap[i]==0:
            dist_pwr_f=0.0
        else:
            dist_pwr_f = (solar_f[i]*solar_cap[i] + wind_f[i]*wind_cap[i]) / total_cap[i]
        power_f = or_fault(central_pwr_f, dist_pwr_f)
        # Total
        total_f = or_fault(network_f,power_f)
        
        failure_rate.append(total_f)
    return failure_rate



def or_fault(f_a, f_b):
    return (f_a + f_b - f_a * f_b)
    
def and_fault(f_a, f_b):
    return (f_a * f_b)

#calculates the % of the population of PR without power
def outage_overall(outage, pop):   
    total_population = 0.0
    failed_population = 0.0
    for i in range(len(pop)):
        ppl_without = outage[i]*pop[i]
        failed_population = failed_population + ppl_without
        total_population = total_population + pop[i]
    return failed_population/total_population