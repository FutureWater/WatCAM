from __future__ import division
import numpy as np
import pandas as pd
import sys


def ReadWPDown(FName, ID):
    '''
    Function to read the ID and flow fraction of water provinces downstream of 
    the given WP
    
    Input
    -----
    FName: string
        Path to the required .csv file.
    ID: integer
        Number of the waterprovince
        
    Output
    -----
    DOWNnr: list of integers
        List of water provinces located downstream of given WP
    DOWNfrac: list of floats
        List of flow fractions towards the downstream WPs, list is in the same
        order as the order of DOWNnr
    '''
    try:
        WP_info = pd.DataFrame.from_csv(FName,header=0)
    except Exception, e:
        print >> sys.stderr, 'Exception: %s' % str(e)
        sys.exit(1)
    #-Adjust column headers
    WP_info.columns = map(str.upper, WP_info.columns)
    #-Locate data corresponding to the ID            
    WP_info = WP_info.loc[ID,]
    #-Empty lists to store downstream IDs and fractions in
    DOWNnr = []
    DOWNfrac = []    
    #-Loop through all downstream WPs, and store the data in the lists
    for i in range(1, WP_info['NR_DOWN']+1):
        DOWNnr += [int(WP_info['TO_ID_'+str(i)])]
        DOWNfrac += [float(WP_info['TO_FRAC_'+str(i)])]
    return DOWNnr, DOWNfrac



def Add_Headflow(FName, ID, Flow, Fraction, StartYY, EndYY):
    '''
    Function to add the outflow of the previously calculated WP to the external
    flow of a WP located downstream

    Input
    -----
    FName: string
        Path to the 'ExtFlow.tss' file. NOTE: this must be without the .npy 
        extension
    ID: int
        ID of the downstream water province
    Flow: numpy.array
        Array of the outflow of the upstream water province
    Fraction: float
        Fracton the Flow that is going to the specified water province
    StartYY: int
        Start year of the calculations
    EndYY: int
        End year of the calculations
        
    Output
    -----
    None -- this function edits the .tss file (given in FName)
        
    '''
    try:
        tss = np.load (FName+'.npy')
    except Exception, e:
        print >> sys.stderr, FName + ' does not exist'
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
    #-Slice the correct column and rows
    PrevFlow = tss[YYstartID:YYendID, colIdx]    
    #-Adjust the new flow, based on the flow fraction and add this to the current value
    NewFlow  = PrevFlow + Flow * Fraction   					# 	 NewFlow  = PrevFlow + Flow  (original)
    #-Replace these values at the right positions
    np.copyto(tss[YYstartID:YYendID, colIdx], NewFlow)
    #-Save the file for later use
    np.save(FName, tss)