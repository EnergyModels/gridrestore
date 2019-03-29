import pandas as pd
import math

#--------------------------------
# Wind turbine and solar farm sizes
#--------------------------------
wt_size = 2.0 # MW
solar_size = 0.3 # MW

#--------------------------------
# Distance between support structures
#--------------------------------
trans_distance = 0.23 # km
dist_distance = 0.042 # km

#--------------------------------
# Import data and extract variables
#--------------------------------
df = pd.read_csv('data.csv')
municipality = df.loc[:,'Node'].values # Name of municipality
regions = df.loc[:,'Region'] # Name of regions

scenarios=['A','B','C','D']
for scenario in scenarios:
    
    #--------------------------------
    # Scenario Inputs
    #--------------------------------
    
    # Defaults
    trans = 'Y' # Include transmission network
    sub = 'Y' # Include substations
    dist = 'Y'   # Include distribution network
        # Solar/Wind/Fossil capacity
    central_fossil = 0.0 # GW
    central_solar = 0.0 # GW
    central_wind = 0.0 # GW
    dist_fossil = 0.0 # GW
    dist_solar = 0.0 # GW
    dist_wind = 0.0 # GW

    if scenario=='A': # Centalized w/ NG
        filename = 'scenarioA'
        central_fossil = 4.2 + 0.7
        
    elif scenario=='B': # Centalized w/ renewables
        filename = 'scenarioB'
        central_fossil = 3.9 + 0.7
        central_solar = 4.1
        central_wind = 1.0

    elif scenario=='C': # Distributed w/ NG
        filename = 'scenarioC'
        trans = 'N' # b/c distributed
        sub = 'N' # b/c distributed
        dist_fossil = 4.2 + 0.7

    elif scenario=='D': # Distributed w/ renewables
        filename = 'scenarioD'
        trans = 'N'
        sub = 'N'
        dist_fossil = 3.17 + 0.7
        dist_solar = 0.0
        dist_wind = 4.4
                
    #--------------------------------
    # Create scenarios
    #--------------------------------
    
    # Copy df
    df2 = df.copy(deep=True)
        
    # Electric network
    if trans=='N':
        df2.loc[:,'Transmission_km'] = 0.0
    if sub=='N':
        df2.loc[:,'Substations'] = 0.0
    if dist=='N':
        df2.loc[:,'Distribution_km'] = 0.0
        
    # Total capacity
    central_total = central_fossil + central_solar + central_wind
    dist_total = dist_fossil + dist_solar + dist_wind
        
    # Create solar and wind
    df2.loc[:,'Solar_MW'] = 0.0
    df2.loc[:,'Wind_MW'] = 0.0
    df2.loc[:,'Total_MW'] = 0.0

    # Create indicator for centralized
    df2.loc[:, 'Central'] = 'N'
    
    # Divide distributed solar and wind (based on population)
    total_pop = sum(df2.loc[:,'Population'])
    for ind in df2.index:
        df2.loc[ind,'Solar_MW'] = dist_solar * 1000.0 * df2.loc[ind,'Population'] / total_pop
        df2.loc[ind,'Wind_MW'] = dist_wind * 1000.0 * df2.loc[ind,'Population'] / total_pop
        df2.loc[ind,'Total_MW'] = dist_total * 1000.0 * df2.loc[ind,'Population'] / total_pop
        
    # Create a centralized node for each region
    for region in regions.unique():
        # ind = regions == region

        ind = df2.loc[:,'Region'] == region
        avg_windspeed =  df2.loc[ind, 'Windspeed_mph'].mean()
        region_pop = df2.loc[ind, 'Population'].sum()

        node = "central_" + region
        df2.loc[node, 'Node'] = node
        df2.loc[node, 'Central'] = 'Y'
        df2.loc[node, 'Region'] = region
        df2.loc[node, 'Population'] = 0.0
        df2.loc[node, 'Windspeed_mph'] = avg_windspeed
        df2.loc[node, 'Transmission_km'] = 0.0
        df2.loc[node, 'Substations'] = 0.0
        df2.loc[node, 'Distribution_km'] = 0.0
        df2.loc[node, 'Solar_MW'] = central_solar * 1000.0 * region_pop / total_pop
        df2.loc[node, 'Wind_MW'] = central_wind * 1000.0 * region_pop / total_pop
        df2.loc[node, 'Total_MW'] = central_total * 1000.0 * region_pop / total_pop

    # Calculate number of wind turbines, solar farms, trans and dist towers
    for ind in df2.index:
        df2.loc[ind,'Solar_farms'] = math.ceil(df2.loc[ind,'Solar_MW'] / solar_size)
        df2.loc[ind,'Wind_turbines'] = math.ceil(df2.loc[ind,'Wind_MW'] / wt_size)
        df2.loc[ind,'Transmission_towers'] = math.ceil(df2.loc[ind,'Transmission_km'] / trans_distance)
        df2.loc[ind,'Distribution_towers'] = math.ceil(df2.loc[ind,'Distribution_km'] / dist_distance)

    # Write to csv
    df2.to_csv(filename + '.csv')