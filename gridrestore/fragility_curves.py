#=============================================================================#
# Fragility Curves
# Written by Claire Trevisan and Jeff Bennett
#=============================================================================#

import numpy as np
import math


# ================================#
# Assess Hurricane Damage
# ================================#

def assess_damage(system, state):

    state.loc[:, 'trans_d'] = trans_damage(system.loc[:, 'Windspeed_ms'], system.loc[:, 'Transmission_Towers'])
    state.loc[:, 'sub_d'] = sub_damage(system.loc[:, 'Windspeed_kmph'], system.loc[:, 'Substations'])
    state.loc[:, 'dist_d'] = dist_damage(system.loc[:, 'Windspeed_ms'], system.loc[:, 'Distribution_Towers'])
    state.loc[:, 'solar_d'] = solar_damage(system.loc[:, 'Windspeed_mph'], system.loc[:, 'Solar_Farms'])
    state.loc[:, 'wind_d'] = wind_damage(system.loc[:, 'Windspeed_knots'], system.loc[:, 'Wind_Turbines'])

    partial_failures = False
    if partial_failures==False:
        state.loc[:, 'trans_d'] = np.ceil(state.loc[:, 'trans_d'])
        state.loc[:, 'sub_d'] = np.ceil(state.loc[:, 'sub_d'])
        state.loc[:, 'dist_d'] = np.ceil(state.loc[:, 'dist_d'])
        state.loc[:, 'solar_d'] = np.ceil(state.loc[:, 'solar_d'])
        state.loc[:, 'wind_d'] = np.ceil(state.loc[:, 'wind_d'])

    return state

# Transmission (per 0.23 km)
trans_x = [43.4483,47.5884,50.6947,53.8032,56.1365,58.7298,60.8059,62.882,64.6994,66.2582,68.0778,69.3766,70.9362,72.2357,73.5359,75.0947,76.3956,77.4365,78.7353,79.7755,80.8149,81.595,82.6352,83.6747,84.9735,86.0129,87.0524,88.0926,89.1313,90.4294,91.7275,92.7676,94.0657,95.6231,97.1806,99.2552,100.553,102.109,103.665,105.22,106.775,108.33,109.626,111.181,112.736,114.807,116.621,118.692,120.504,122.575,123.611,124.904,126.198,127.493,129.304,131.633,133.444,134.996,136.808,138.619,140.43,142.758,145.344,147.414]
trans_y = [0.00E+00,0.00837677,0.0195248,0.0388921,0.060952,0.0885071,0.116031,0.143554,0.171062,0.198555,0.234282,0.256279,0.286511,0.311247,0.338724,0.366216,0.396432,0.421153,0.44315,0.465131,0.484372,0.500858,0.522839,0.542081,0.564078,0.583319,0.60256,0.624541,0.641043,0.6603,0.679557,0.701538,0.720795,0.742808,0.764821,0.786865,0.806122,0.819915,0.836448,0.850242,0.864035,0.875089,0.888866,0.89992,0.910973,0.922058,0.933128,0.941473,0.947063,0.955408,0.96095,0.963769,0.966587,0.972146,0.974996,0.980617,0.983467,0.986301,0.989151,0.992001,0.994851,0.997733,0.99789,1]
def trans_damage(wind_ms, trans_length):
    # p_failure = -2.710735810338340000E-12*wind_ms**6 + 1.647468005219630000E-09*wind_ms**5 - 3.746345175184950000E-07*wind_ms**4 + 3.816483952242150000E-05*wind_ms**3 - 1.585646768797350000E-03*wind_ms**2 + 2.229472752851760000E-02*wind_ms - 5.056075618431450000E-02

    p_failure = np.interp(wind_ms, trans_x, trans_y)
    damaged_length = []
    for i in range(len(p_failure)):
        p = p_failure[i]
        if p<0:
            length= 0.0
            damaged_length.append(length)
        else:
            length = p*trans_length[i]
            damaged_length.append(length)
    return damaged_length

# Substation
sub_x = [40.1487,60.223,80.2974,100.372,119.703,139.777,159.851,179.926,200.0,220.074,240.149,260.223,281.041,301.115]
sub_y = [0.0,0.0136986,0.0228311,0.0273973,0.0456621,0.0639269,0.0913242,0.13242,0.214612,0.424658,0.648402,0.803653,0.890411,0.931507]
def sub_damage(wind_kmph, substations):
    # p_failure = -3.801409548821570000E-15*wind_kmph**6 - 6.113514503951920000E-12*wind_kmph**5 + 5.050350469857500000E-09*wind_kmph**4 - 1.119598812160390000E-06*wind_kmph**3 + 9.567764706108760000E-05*wind_kmph**2 - 2.480663283861870000E-03*wind_kmph + 5.875565991175340000E-03

    p_failure = np.interp(wind_kmph, sub_x, sub_y)
    damaged_subs = []
    for i in range(len(p_failure)):
        p = p_failure[i]
        if p<0:
            sub= 0.0
            damaged_subs.append(sub)
        else:
            sub = p*substations[i]
            damaged_subs.append(sub)
    return damaged_subs

# Distribution
dist_x = [34.375,38.1855,40.3024,42.2782,45.3831,48.3468,50.4637,52.0161,53.7097,55.2621,57.379,59.2137,60.9073,62.4597,63.871,65.5645,67.3992,68.8105,70.3629,72.1976,75.0202,77.7016,80.3831,83.2056,86.1694,89.2742,96.8952]
dist_y = [0.0,0.0133333,0.0311111,0.0533333,0.102222,0.173333,0.235556,0.284444,0.342222,0.395556,0.471111,0.533333,0.591111,0.635556,0.68,0.728889,0.773333,0.8,0.831111,0.862222,0.902222,0.937778,0.964444,0.982222,0.991111,0.995556,1.0]
def dist_damage(wind_ms,dist_length):
    # p_failure = -0.000000000255390841*wind_ms**6 + 0.000000103423463477*wind_ms**5 - 0.000016709417266960*wind_ms**4 + 0.001361824166163350*wind_ms**3 - 0.058282700178697800*wind_ms**2 + 1.245779805212810000*wind_ms - 10.480160018737900000

    p_failure = np.interp(wind_ms, dist_x, dist_y)
    damaged_length = []
    for i in range(len(p_failure)):
        p = p_failure[i]
        if p<0:
            length= 0.0
            damaged_length.append(length)
        else:
            length = p*dist_length[i]
            damaged_length.append(length)
    return damaged_length

# Solar Energy
solar_x = np.array([90.0,110.2020202,130.0,150.0,170]) + 30.0
solar_y = [0.0,0.106145251,0.525139665,0.865921788,1.0]
  
def solar_damage(wind_mph, solar_infra):
    
    p_failure = np.interp(wind_mph, solar_x, solar_y)
    
    damaged_solar = []
    for i in range(len(p_failure)):
        p = p_failure[i]
        if p<0:
            damaged = 0.0
            damaged_solar.append(damaged)
        else:
            damaged = p*solar_infra[i]
            damaged_solar.append(damaged)
    return damaged_solar

# Wind Energy (Yawing)
# https://www.pnas.org/content/pnas/suppl/2012/02/07/1111769109.DCSupplemental/pnas.1111769109_SI.pdf?targetid=STXT
#wind_x = [120.0657132,124.3653638,128.6646451,132.3713997,136.0777849,139.7836162,143.9335195,147.3418872,150.0079808,152.6744437,154.8949881,156.671276,160.5181763,163.1789151,165.5436676,168.3517534,171.4532406,173.2241738,176.4737465,179.2785087,182.9732613,184.7471488,187.5563425,191.404166,193.6245258,196.1416106,199.1036906,202.2151487,205.1788905,209.180339,212.7375308,216.2950919,219.7045675]
#wind_y = [0,0.00124533,0.00498132,0.00498132,0.00747198,0.01369863,0.0249066,0.0373599,0.056039851,0.072229141,0.095890411,0.115815691,0.170610212,0.225404732,0.276463263,0.337484433,0.419676214,0.475716065,0.559153176,0.642590286,0.723536737,0.759651308,0.813200498,0.861768369,0.886674969,0.910336239,0.932752179,0.947696139,0.95890411,0.97135741,0.98007472,0.98630137,1]

# Wind Energy (Non-Yawing)
wind_x = [97.38019084,101.0869454,108.7957023,116.0578022,120.2056744,123.7586193,128.1954614,131.2997183,133.5139848,135.5818276,137.2039366,139.5655501,141.0403122,142.6635291,144.1390297,145.9107014,147.9785442,149.8997786,151.9694679,154.3364361,157.1482148,160.4059119,164.7018696,169.4437458,175.0759815,180.8574107,188.5670909,194.7940692]
wind_y = [0,0.00124533,0.00996264,0.03113325,0.056039851,0.093399751,0.169364882,0.232876712,0.298879203,0.352428394,0.412204234,0.484433375,0.537982565,0.590286426,0.638854296,0.689912827,0.743462017,0.785803238,0.826899128,0.863013699,0.899128269,0.927770859,0.95392279,0.97260274,0.98630137,0.99377335,0.99626401,1]

def wind_damage(wind_knots, wind_infra):
    
    p_failure = np.interp(wind_knots, wind_x, wind_y)

    damaged_wind = []
    for i in range(len(p_failure)):
        p = p_failure[i]
        if p<0:
            damaged = 0.0
            damaged_wind.append(damaged)
        else:
            damaged = p*wind_infra[i]
            damaged_wind.append(damaged)
    return damaged_wind