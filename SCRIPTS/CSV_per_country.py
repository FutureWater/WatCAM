from __future__ import division
import pandas as pd
import numpy as np
import sys

#%% SETUP
pathIN = r'C:\TEMP'
pathIN += '\\'
scen = ['RCP_2.6','SSP1']

ALLoutputType = ['GROSS_dem_DOM','GROSS_dem_IND','GROSS_dem_IRR','GROSS_dem_ENV',
                 'ACTUAL_withdrawal_DOM','ACTUAL_withdrawal_IND','ACTUAL_withdrawal_IRR','ACTUAL_withdrawal_ENV',
                 'UNMET_DOM','UNMET_IND','UNMET_IRR','UNMET_ENV',
                 'RETURN_DOM','RETURN_IND','RETURN_IRR','RETURN_ENV',
                 'CONSUMED_DOM','CONSUMED_IND','CONSUMED_IRR','CONSUMED_ENV']

#%% PARAMS
pars = pd.read_csv(r'c:\Users\Joost\Dropbox\W2I_Demo\MODEL\WatCam2016\WATCAM_paper\Param3.02\Adpt_0.csv',header=1)
pars = pars.set_index(pars['WatProvID'])
allWPs = range(1,1605)
RCP = scen[0]
SSP = scen[1]

#%% SUM VALUES
summedWP = pd.DataFrame()        

for outputType in ALLoutputType:
    print outputType
    shp_csv = pd.DataFrame()
    for WP in allWPs:       
        
        # For checking purposes later on
        df = 0        
        # Define the filename of the output csv
        FName = pathIN + RCP + '_' + SSP + '\\WP_{:04d}'.format(WP) + '.csv'
        
        # Test whether this file exists, since not all WP numbers are in use
        try:
            df = pd.read_csv(FName,header=0)
        except IOError:
            pass
        
        # Test whether df has been updated to a DataFrame, or is still an int
        if type(df) == type(pd.DataFrame()):
    
            pStart = 0
            pEnd = 120
            ave_p1 = sum(df[outputType][pStart:pEnd])/((pEnd-pStart)/12)                
            OUT = pd.Series([ave_p1])            
            shp_csv[WP] = OUT
            
    shp_csv = shp_csv.T
    shp_csv.index.names = ['WatProvID']
    shp_csv.columns = [outputType+'.Base']
    
    summedWP = pd.concat([summedWP,shp_csv],axis=1)

#%% Link countries with WP_IDs
countries = pd.read_csv("C:\Users\Joost\Dropbox\W2I_Demo\PAPER\DATA\COUNTRY_lookup.csv")
countriesUnique = list(set(countries.COUNTRY))

summedCOUNTRY = pd.DataFrame()
for country in countriesUnique:
    # Create emtpy Series to store summed data
    summed = pd.Series([0.0]*len(list(summedWP.columns))) 
    summed.index = list(summedWP.columns)
    for index, data in countries.iterrows():
        if data.COUNTRY == country:
            try:
                summed += summedWP.loc[data.ID,]
            except:
                pass

    summedCOUNTRY[country] = summed
summedCOUNTRY = summedCOUNTRY.T
summedCOUNTRY = summedCOUNTRY.sort_index()

summedCOUNTRY.to_csv("C:\Users\Joost\Dropbox\W2I_Demo\PAPER\RESULTS\CSVs\RCP26_SSP1_adpt0.csv")