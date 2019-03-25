#=============================================================================#
# Fragility Curves
# Written by Claire Trevisan and Jeff Bennett
#=============================================================================#

import numpy as np

# Distribution
def dist_damage(wind_ms,dist_length):
    p_failure = -0.000000000255390841*wind_ms**6 + 0.000000103423463477*wind_ms**5 - 0.000016709417266960*wind_ms**4 + 0.001361824166163350*wind_ms**3 - 0.058282700178697800*wind_ms**2 + 1.245779805212810000*wind_ms - 10.480160018737900000
    # fragility: y = -0.000000000255390841x6 + 0.000000103423463477x5 - 0.000016709417266960x4 + 0.001361824166163350x3 - 0.058282700178697800x2 + 1.245779805212810000x - 10.480160018737900000 
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

# Transmission (per 0.23 km)
def trans_damage(wind_ms,trans_length):
    p_failure = -2.710735810338340000E-12*wind_ms**6 + 1.647468005219630000E-09*wind_ms**5 - 3.746345175184950000E-07*wind_ms**4 + 3.816483952242150000E-05*wind_ms**3 - 1.585646768797350000E-03*wind_ms**2 + 2.229472752851760000E-02*wind_ms - 5.056075618431450000E-02
     # fragility: y = -2.710735810338340000E-12x6 + 1.647468005219630000E-09x5 - 3.746345175184950000E-07x4 + 3.816483952242150000E-05x3 - 1.585646768797350000E-03x2 + 2.229472752851760000E-02x - 5.056075618431450000E-02 
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
def sub_damage(wind_kmph, substations):
    p_failure = -3.801409548821570000E-15*wind_kmph**6 - 6.113514503951920000E-12*wind_kmph**5 + 5.050350469857500000E-09*wind_kmph**4 - 1.119598812160390000E-06*wind_kmph**3 + 9.567764706108760000E-05*wind_kmph**2 - 2.480663283861870000E-03*wind_kmph + 5.875565991175340000E-03 
    # fragility: y = -3.801409548821570000E-15x6 - 6.113514503951920000E-12x5 + 5.050350469857500000E-09x4 - 1.119598812160390000E-06x3 + 9.567764706108760000E-05x2 - 2.480663283861870000E-03x + 5.875565991175340000E-03 
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