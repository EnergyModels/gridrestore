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
municipality = df.iloc[:,0].values # Name of municipality

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
        df2.loc[:,'Trans LENGTH km'] = 0.0
    if sub=='N':
        df2.loc[:,'Substations'] = 0.0
    if dist=='N':
        df2.loc[:,'DistLineLength km'] = 0.0
        
    # Total capacity
    central_total = central_fossil + central_solar + central_wind
    dist_total = dist_fossil + dist_solar + dist_wind
        
    # Create solar and wind
    df2.loc[:,'Solar_MW'] = 0.0
    df2.loc[:,'Wind_MW'] = 0.0
    df2.loc[:,'Total_MW'] = 0.0
    
    # Divide distributed solar and wind (based on population)
    total_pop = sum(df2.loc[:,'County Population']) 
    for ind in df2.index:
        df2.loc[ind,'Solar_MW'] = dist_solar * 1000.0 * df2.loc[ind,'County Population'] / total_pop
        df2.loc[ind,'Wind_MW'] = dist_wind * 1000.0 * df2.loc[ind,'County Population'] / total_pop
        df2.loc[ind,'Total_MW'] = dist_total * 1000.0 * df2.loc[ind,'County Population'] / total_pop 
        
    # Divide centralized solar and wind
    central_dummies = ['central_dummy1','central_dummy2','central_dummy3','central_dummy4']
    for central_dummy in central_dummies:
        ind = municipality==central_dummy
        df2.loc[ind,'Solar_MW'] = central_solar / 4.0 * 1000.0
        df2.loc[ind,'Wind_MW'] = central_wind / 4.0 * 1000.0
        df2.loc[ind,'Total_MW'] = central_total / 4.0 * 1000.0

    # Calculate number of wind turbines, solar farms, trans and dist towers
    for ind in df2.index:
        df2.loc[ind,'Solar_farms'] = math.ceil(df2.loc[ind,'Solar_MW'] / solar_size)
        df2.loc[ind,'Wind_turbines'] = math.ceil(df2.loc[ind,'Wind_MW'] / wt_size)
        df2.loc[ind,'Trans_towers'] = math.ceil(df2.loc[ind,'Trans LENGTH km'] / trans_distance)
        df2.loc[ind,'Dist_towers'] = math.ceil(df2.loc[ind,'DistLineLength km'] / dist_distance)

    # Write to csv
    df2.to_csv(filename + '.csv')