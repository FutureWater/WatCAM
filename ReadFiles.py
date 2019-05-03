from __future__ import division
import numpy as np
import pandas as pd
import sys
import os
#import logging

def ReadParamFile(FName, ID):
    """
    Read csv file and converts it to a pandas DataFrame.
    
    Input
    -----
    path: string
        Path to parameter file
    WP_number: int
        Number of the required water province
    
    Output
    -----
    pars: pandas.DataFrame
        Dataset with all the required parameter values, for the given water province
        
    """
    try:
        pars = pd.read_csv(FName,header=1,index_col=0)
        pars = pars.loc[[ID],:]
        return pars.to_dict('records')[0]   #pass pars as dict instead of dictionary to gain speed
        
    except Exception, e:
        print >> sys.stderr, 'Exception: %s' % str(e)
        sys.exit(1)

def ReadWatProvIDs(FName):
    '''
    Function to read which WPs need to be ran. Loops through .csv file
    where for each WP a 'Y' or 'N' is defined.
    
    Input
    -----
    FName: string
        Path to the required .csv file.
        
    Output
    -----
    order_ID: list of lists
        Each internal list contains is formatting as follows: [[CALC_order, WP_ID], ...].
        Here the first item contains the calculation order, and the second item
        the water province ID (all the IDs where a 'Y' is selected in the.csv
        file)
    '''
    try:
        WP_info = pd.read_csv(FName,header=0)
    except Exception, e:
        print >> sys.stderr, 'Exception: %s' % str(e)
        sys.exit(1)
    WP_info.sort_values(by='ORDER',inplace=True)
    order_ID = WP_info.loc[WP_info[' CALC']=='Y',:].as_matrix(['ORDER','ID'])

    return order_ID


def ReadInputFiles(workdir, dir_RCP, dir_SSP, dir_GEN, ID, StartYY, EndYY):
    '''
    This function reads all the required input (.tss.npy) files, given for the
    right scenario, water province and the correct start and end dates.
    
    Input
    -----
    workdir: string
        Path of the .../WatCAM/Input/ directory
    dir_RCP: string
        Name of the folder corresponding to the correct RCP scenario
    dir_SSP: string
        Name of the folder corresponding to the correct SSP scenario
    dir_GEN: string
        Name of the folder corresponding to the correct general data (historic
        of future)
    ID: integer
        Number of the required water province
    StartYY: integer
        Year to start calculations
    EndYY: integer
        Last year to perform calculations
        
    Output
    ------
    INPUT: pandas.DataFrame
        DataFrame containing the following columns
        
        ['YY', 'MM', 'FLO_internal_org', 'RES_capacity_org', 'IND_demand_org', 
        'FLO_pristine', 'IRR_area_org', 'ET_ref', 'GWT_capacity', 'FLO_external', 
        'DWN_demand', 'Population', 'DOM_demand_org']
        
    '''
    
    input_files = {
        'Population'        : os.path.join(dir_SSP, 'population.tss'),
        'DOM_demand_org'    : os.path.join(dir_SSP, 'dom_l_p_day.tss'),
        'IND_demand_org'    : os.path.join(dir_SSP, 'demIndustry_m3.tss'),
        'IRR_area_org'      : os.path.join(dir_GEN, 'irr_area_m2.tss'),
        'ET_ref'            : os.path.join(dir_RCP, 'Etref_mm.tss'),
        'DWN_demand_org'    : os.path.join(dir_GEN, 'ZERO.tss'),
        'FLO_internal_org'  : os.path.join(dir_RCP, 'IntFlow.tss'),
        'FLO_external_org'  : os.path.join(dir_RCP, 'ExtFlow.tss'),
        'RES_capacity_org'  : os.path.join(dir_GEN, 'Res_cap.tss'),
        'GWT_capacity'      : os.path.join(dir_GEN, 'GW_cap.tss'),
        'FLO_pristine'      : os.path.join(dir_GEN, 'Hist_Flo_m3.tss'),
        'GW_recharge'       : os.path.join(dir_RCP, 'Q3_km3.tss')}

    INPUT = pd.DataFrame()
    
    INPUT['YY'] = [item for item in range(StartYY,EndYY+1) for i in range(12)]
    INPUT['MM'] = [item for i in range(StartYY,EndYY+1) for item in range(1,13)]
    
    for key in input_files:
        INPUT[key] = ReadTSS(os.path.join(workdir, input_files[key]), ID, StartYY, EndYY)
        if key == 'GW_recharge':
            INPUT['Average_rech'] = AverageRECH(os.path.join(workdir, input_files[key]),ID,2006,2015)    

    # convert dataframe to dictionary of np.array to enhance computational performance
    INPUT = INPUT.to_dict('list')
    for key, value in INPUT.iteritems():
        INPUT[key] = np.array(value)
        
    return INPUT

def ReadTSS(FName, ID, StartYY, EndYY):
    '''
    Function to read .tss.npy files. Returns a time series for the corresponding
    WP, over the relevant period. 
    
    Input
    -----
    FName: string
        Path to the .tss.npy file
    ID: integer
        Number/ID of the water province
    startYY: integer
        First year of the required period
    endYY: integer
        Last year of the required period
        
    Output
    ------
    average_rech: float
        Average baseflow for the corresponding WP, calculated over the defined
        period. This value is used as the recharge within WatCAM
    ''' 
    try:
        FName = FName + '.npy'
        tss = np.load(FName)
    except Exception, e:
        print >> sys.stderr, 'Exception: %s' % str(e)
        sys.exit(1)

    #-Extract the time series data for 'ID' from the tss array AND for the years
    #-Retrieve top row from file, except first 4 cols, these are placeholders
    IDs = tss[0,4:]
    # Find right column, add 4 for the first 4 placeholder columns (YYYY, MM, DD, DD)
    colIdx = 4 + np.searchsorted(IDs, int(ID))
    #-Retrive the column containing the year values, except the first 3 rows, these are placeholders
    YY  = tss[3:, 0]
    #-Find the right starting row, add 3 for the placeholder rows
    YYstartID = 3 + np.searchsorted(YY, StartYY)
    #-Calculate the number of months inbetween
    YYendID   = YYstartID + ((EndYY - StartYY + 1) * 12)
    #-Slice the right column and section of rows
    Col = tss[YYstartID:YYendID , colIdx]
    return Col

def AverageRECH(FName,ID,startBASE = 2006,endBASE = 2015):
    '''
    This function reads the baseflow output from PCR-GLOBWB, and calculates the
    average baseflow over the period defined by a start and end date, for the 
    relevant water province
    
    Input
    -----
    FName: string
        Path to the Q3_km3.tss.npy file
    ID: integer
        Number/ID of the water province
    startBASE: integer
        First year of the period (default = 2006)
    endBASE: integer
        Last year of the period (default = 2015)
        
    Output
    ------
    average_rech: float
        Average baseflow for the corresponding WP, calculated over the defined
        period. This value is used as the recharge within WatCAM
    ''' 
    rech = ReadTSS(FName,ID,startBASE,endBASE)
    average_rech = sum(rech)/len(rech)    
    average_rech *= 1e9
    return average_rech