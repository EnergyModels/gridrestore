#=============================================================================#
# Grid Restoration Model
# Written by Claire Trevisan and Jeff Bennett
#=============================================================================#
import pandas as pd
import numpy as np
from pandas import ExcelWriter
from fragility_curves import dist_damage, trans_damage, sub_damage, solar_damage, wind_damage
from support_functions import percent_failed, outage_municip, outage_overall
import matplotlib.pyplot as plt

debug = True


scenarios = ['A','B','C','D']

#scenarios = ['D']

for scenario in scenarios:
    
    # Defaults
    central_solar = 0.0
    central_wind = 0.0
    dist_solar = 0.0
    dist_wind = 0.0
    
    # Scenario specific inputs
    if scenario == 'A':
        filename = 'scenarioA'
    
    elif scenario == 'B':
        filename = 'scenarioB'
        central_solar = 20.0
        central_wind = 20.0
    
    elif scenario == 'C':
        filename = 'scenarioC'
    
    elif scenario == 'D':
        filename = 'scenarioD'
        dist_solar = 20.0
        dist_wind = 20.0
    
    
    # Repair time inputs
    #daily_hours = 60000 # hours for 1000 crew members working 60 hours a week
    #time_dist = 119.0 # hours to repair one km of distribution (Ouyang et al 2014)
    #time_trans = 313.0 # hours to repair one km of transmission (Ouyang et al 2014)
    #time_sub = 168.0 # hours to repair one sub (Ouyang et al 2014)
    #time_solar = 7.5 # non-electrician work hours, source: http://energyinformative.org/solar-panels-installation-time
    #time_wind = 10.0
    
    
    # Repair time (cost) inputs
    daily_hours = 10.8E6 #10 million per day
    time_trans = 0.4E6 # cost to repair transmission structure(Ouyang et al 2014)
    time_dist = 2500.0 # cost to repair one distribution pole (Ouyang et al 2014)
    time_sub = 5.5E6 # cost to repair one substation (moderate) (Ouyang et al 2014)
    time_solar = 850.0 # non-electrician work hours, source: http://energyinformative.org/solar-panels-installation-time
    time_wind = 1750000.0
    
    # Import data and extract variables
    df = pd.read_csv(filename + '.csv')
    municipality = df.loc[:,"NAMELSAD"].values # Name of municipality
    population = df.loc[:,"County Population"].values # Population (-)
    wind_mph = df.loc[:,"Max Peak (mph)"].values # Windspeed (miles per hour)
    trans = df.loc[:,"Trans_towers"].values # Transmission lines (miles per municipality)
    sub = df.loc[:,"Substations"].values # Substations (# per municipality)
    dist = df.loc[:,"Dist_towers"].values # Distribution lines (miles per municipality)
    
    solar_cap = df.loc[:,"Solar_MW"].values # Solar MW (# per municipality)
    wind_cap = df.loc[:,"Wind_MW"].values # Wind MW (# per municipality)
    total_cap = df.loc[:,"Total_MW"].values# Total MW (# per municipality)
    solar = df.loc[:,"Solar_farms"].values # Solar farms (# per municipality)
    wind = df.loc[:,"Wind_turbines"].values# Wind turbines (# per municipality)
    
    # Convert windspeed to m/s and km/h
    wind_ms = wind_mph*0.44704
    wind_kmh = wind_mph*1.60934
    wind_knots = wind_mph/1.15078
    
    # Initial damage
    damaged_trans = trans_damage(wind_ms, trans)
    damaged_sub = sub_damage(wind_kmh, sub)
    damaged_dist = dist_damage(wind_ms, dist)
    damaged_solar = solar_damage(wind_mph, solar)
    damaged_wind = wind_damage(wind_knots, wind)
    
    # Total Repair cost
    total_cost_municip =  time_trans * np.array(damaged_trans) + time_sub * np.array(damaged_sub) + time_dist * np.array(damaged_dist) + time_solar * np.array(damaged_solar) + time_wind * np.array(damaged_wind)
    total_cost =  sum(total_cost_municip) / 1E6 # Million (M$)
    total_time = total_cost * 1E6 / daily_hours
    
    # Initial failure percentages
    init_f_trans = percent_failed(damaged_trans, trans)
    init_f_sub = percent_failed(damaged_sub, sub)
    init_f_dist = percent_failed(damaged_dist, dist)
    init_f_solar = percent_failed(damaged_solar, solar)
    init_f_wind = percent_failed(damaged_wind, wind)
    
    # Initial cumulative outage
    n_central = 4 # First four municipalities are actually dummy placeholders to hold centralized generation
    outage_prob_municip = outage_municip(n_central, init_f_trans, init_f_sub, init_f_dist, init_f_solar, init_f_wind, solar_cap, wind_cap, total_cap)
    init_outage_prob_municip = outage_municip(n_central, init_f_trans, init_f_sub, init_f_dist, init_f_solar, init_f_wind, solar_cap, wind_cap, total_cap)
    PR_outage = outage_overall(outage_prob_municip,population)
    #
    # Prioritize repair based on municipalities with highest outages
    sort_order = np.argsort(outage_prob_municip*population)
    sort_order = np.append(sort_order,range(n_central)) # Prioritize centralized pwoer plants over distributed
    
    # Prepare variables to track during simulation
    unrestored_trans = damaged_trans
    unrestored_sub = damaged_sub
    unrestored_dist = damaged_dist
    unrestored_solar = damaged_solar
    unrestored_wind = damaged_wind
    
    recovery_outage = [outage_overall(outage_prob_municip,population)]
    restoration = [1.0-outage_overall(outage_prob_municip,population)]
    
    if debug==True:
        f = open("debug_" + filename + ".txt","w")
    
    times = [0.0]
    costs = [0.0]
    t = 0.0
    while PR_outage>0.001:
        
        t = t+1.0
        hours = 0.0
        
        if debug==True:
            f.write("#==========================#\nTime " + str(t) + '\n#==========================#\n')
            
        #-------------------------------------------------------------------------
        # Transmission lines
        #------------------------------------------------------------------------- 
        if hours < daily_hours:
            
            if debug==True and sum(unrestored_trans)>0:
                f.write("Repairing transmission lines---" + '\n\n')
            
            for i in reversed(sort_order):
                
                # Check if work time left for the day, and repair is necessary
                if hours < daily_hours and unrestored_trans[i]>0:
                    
                    # Maximum number of miles repairable for the current day and municipality
                    repairable = (daily_hours-hours)/time_trans
                    
                    if debug == True:
                        f.write("Municipality #: " + str(i) + '\n')
                        f.write("Repairable miles                 : " + str(round(repairable,2))  + '\n')
                        f.write("Starting - unrestored trans miles: " + str(round(unrestored_trans[i],2))  + '\n')
                        
                    # Check if the entire municipalicty can be repaired
                    if repairable < unrestored_trans[i]:
                        unrestored_trans[i] = unrestored_trans[i]-repairable
                        hours = daily_hours
                        repaired=repairable
                        
                    else: 
                        hours = hours + unrestored_trans[i]*time_trans
                        repaired = unrestored_trans[i]
                        unrestored_trans[i] = 0.0
                    
                    if debug == True:
                        f.write("Miles repaired                   : " + str(round(repaired,2)) + '\n')
                        f.write("Updated - unrestored trans miles : " + str(round(unrestored_trans[i],2)) + '\n\n')
        
        #-------------------------------------------------------------------------
        # Substations
        #------------------------------------------------------------------------- 
    
        if hours < daily_hours:     
            
            if debug==True and sum(unrestored_sub)>0:
                f.write("Repairing substations---"+ '\n')   
                
            for i in reversed(sort_order):
                if hours < daily_hours and unrestored_sub[i]>0:
                    
                    repairable = (daily_hours-hours)/time_sub
                    if debug == True:
                        f.write("Municipality #: " + str(i)+ '\n')
                        f.write("Repairable stations              : " + str(round(repairable,2))+ '\n')
                        f.write("Starting - unrestored substations: " + str(round(unrestored_sub[i],2))+ '\n')
                        
                    if repairable < unrestored_sub[i]:
                        unrestored_sub[i] = unrestored_sub[i]-repairable
                        hours = daily_hours
                        repaired = repairable
                    else: 
                        hours = hours + unrestored_sub[i]*time_sub
                        repaired = unrestored_sub[i]
                        unrestored_sub[i] = 0.0
                    
                    if debug == True:
                        f.write("Substations repaired             : " + str(round(repaired,2))+ '\n')
                        f.write("Updated - unrestored substations : " + str(round(unrestored_sub[i],2)) + '\n\n')
                    
                    
        #-------------------------------------------------------------------------
        # Distribution lines
        #-------------------------------------------------------------------------                
    
        if hours < daily_hours:
            if debug==True and sum(unrestored_dist)>0:
                f.write( "Repairing distribution lines---"+ '\n')
            
            for i in reversed(sort_order):
                if hours < daily_hours and unrestored_dist[i]>0:
                    repairable = (daily_hours-hours)/time_dist
    
                    if debug == True:
                        f.write("Municipality #: " + str(i) + '\n')
                        f.write("Repairable miles                 : " + str(round(repairable,2)) + '\n')
                        f.write("Starting - unrestored dist miles : " + str(round(unrestored_dist[i],2))+ '\n')
    
                    if repairable < unrestored_dist[i]:
                        unrestored_dist[i] = unrestored_dist[i]-repairable
                        hours = daily_hours
                        repaired = repairable
                    else:
                        hours = hours + unrestored_dist[i]*time_dist
                        repaired = unrestored_dist[i]
                        unrestored_dist[i] = 0.0
                    
                    if debug == True:
                        f.write("Miles repaired                   : " + str(round(repaired,2))+ '\n')
                        f.write("Updated - unrestored dist miles  : " + str(round(unrestored_dist[i],2)) + '\n\n')
                    
        #-------------------------------------------------------------------------
        # Solar panels
        #------------------------------------------------------------------------- 
        if debug==True and sum(unrestored_solar)>0:    
            f.write( "Repairing solar---"+ '\n')
        if hours < daily_hours:
            for i in reversed(sort_order):
                
                if hours < daily_hours and unrestored_solar[i]>0:
                    repairable = (daily_hours-hours)/time_solar
                    
                    if debug == True:
                        f.write( "Municipality #: " + str(i)+ '\n')
                        f.write( "Repairable solar                 : " + str(repairable)+ '\n')
                        f.write( "Starting - unrestored solar      : " + str(unrestored_solar[i])+ '\n')
                        
                    if repairable < unrestored_solar[i]:
                        unrestored_solar[i] = unrestored_solar[i]-repairable
                        hours = daily_hours
                        repaired = repairable
                    else: 
                        hours = hours + unrestored_solar[i]*time_solar
                        repaired = unrestored_solar[i]
                        unrestored_solar[i] = 0.0
                    
                    if debug == True:
                        f.write( "Solar repaired                   : " + str(repaired)+ '\n')
                        f.write( "Updated - unrestored solar       : " + str(unrestored_solar[i])+ '\n\n')
                    
        #-------------------------------------------------------------------------
        # Wind turbines
        #------------------------------------------------------------------------- 
        if debug==True and sum(unrestored_wind)>0:    
            f.write( "Repairing wind---"+ '\n')
        if hours < daily_hours:
            for i in reversed(sort_order):
                
                if hours < daily_hours and unrestored_wind[i]>0:
                    repairable = (daily_hours-hours)/time_wind
                    
                    if debug == True:
                        f.write( "Municipality #: " + str(i)+ '\n')
                        f.write( "Repairable wind                  : " + str(repairable)+ '\n')
                        f.write( "Starting - unrestored wind       : " + str(unrestored_wind[i])+ '\n')
                        
                    if repairable < unrestored_wind[i]:
                        unrestored_wind[i] = unrestored_wind[i]-repairable
                        hours = daily_hours
                        repaired = repairable
                    else: 
                        hours = hours + unrestored_wind[i]*time_wind
                        repaired = unrestored_wind[i]
                        unrestored_wind[i] = 0.0
                    
                    if debug == True:
                        f.write( "Wind repaired                    : " + str(repaired)+ '\n')
                        f.write( "Updated - unrestored wind        : " + str(unrestored_wind[i])+ '\n\n')
                    
        # Calculate new outage
        trans_f = percent_failed(unrestored_trans, trans)
        sub_f = percent_failed(unrestored_sub, sub)
        dist_f = percent_failed(unrestored_dist, dist)
        solar_f = percent_failed(unrestored_solar, solar)
        wind_f = percent_failed(unrestored_wind, wind)
        
        municip_out = outage_municip(n_central, trans_f, sub_f, dist_f, solar_f, wind_f, solar_cap, wind_cap, total_cap)
        PR_outage = outage_overall(municip_out,population)
        if debug==True:
            f.write("PR_outage (%): " + str(round(100*PR_outage,2)) + '\n')
            f.write("With power (%): " + str(round(100.0-100*PR_outage,2)) + '\n')
            
        # Save results
        times.append(t)
        costs.append(hours)
        PR_restore = 1.0-PR_outage
        restoration.append(PR_restore)
        recovery_outage.append(PR_outage)    
        
        # Update sort order based on current outages
    #    sort_order = np.argsort(municip_out)
    
    # Write to console
    print "Scenario                 : " + filename
    print "Total Repair time (weeks): " + str(t/7.0)
    print "Total Repair time (weeks): " + str(total_time/7.0)
    print "Total Cost (M$): " + str(total_cost) + '\n'
        
    # Save and plot data
    if debug==True:
        f.write("#======================#\n")
        f.write("Total Repair time (weeks): " + str(t/7.0) + "\n")
        f.write("Total Repair time (weeks): " + str(total_time/7.0) + "\n")
        f.write("Total Cost (M$): " + str(total_cost) + "\n")
        f.write("#======================#\n")
        f.close()
        
    # Create Plot
    df_restore = pd.DataFrame({"% With Power":restoration,"Day":times, "Cost":costs})
    df_restore.plot().set_xlabel("Time (weeks)")
    plt.savefig('Results_' + filename + '.png')
    plt.close()
    
    # Save to XLSX
#    writer = ExcelWriter('Results_' + filename + '.xlsx')
    df_restore.to_csv('Results_' + filename + '.csv')
#    writer.save()

