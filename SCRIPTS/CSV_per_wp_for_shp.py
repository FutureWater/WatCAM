from __future__ import division
import pandas as pd
import sys
import numpy as np

def create_shp_csv(pathIN,scen,pathOUT):

    ALLoutputType = ['FLO_internal','FLO_external','FLO_ava','FLO_extracted','RES_extracted','GWT_storage','GWT_inflow','GWT_extracted',
                     'GROSS_dem_DOM','GROSS_dem_IND','GROSS_dem_IRR','GROSS_dem_ENV',
                     'UNMET_DOM','UNMET_IND','UNMET_IRR','UNMET_ENV']

#    ALLoutputType = ['FLO_internal']
    
    
    pars = pd.read_csv(r'c:\Users\Joost\Dropbox\W2I_Demo\MODEL\WatCam2016\WATCAM_paper\Param\Adpt_0.csv',header=1)
    pars = pars.set_index(pars['WatProvID'])

    allWPs = range(1,1605)
        
    FName = r'c:\Users\Joost\Dropbox\W2I_Demo\MODEL\WatCam2016\WATCAM_paper\Input\General_FUT\GW_cap.tss.npy'
    GW_cap = np.load(FName)
    GW_cap = pd.DataFrame(data=GW_cap[1:,0:],columns=GW_cap[0,0:])    
    cols = ['YY','D1','D2','D3'] + list(GW_cap.columns[4:])
    GW_cap.columns = cols
    
    RCP = scen[0]
    SSP = scen[1]    
    
    FName = r'c:\Users\Joost\Dropbox\W2I_Demo\MODEL\WatCam2016\WATCAM_paper\Input\\'+SSP+r'\population.tss.npy'
    POP = np.load(FName)
    POP = pd.DataFrame(data=POP[1:,0:],columns=POP[0,0:])    
    cols = ['YY','D1','D2','D3'] + list(POP.columns[4:])
    POP.columns = cols
    
    for outputType in ALLoutputType:
        print scen, outputType
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
        
                p1 = 120
                p2_s = df.YY[df.YY == 2020].index.tolist()[0]
                p2_e = df.YY[df.YY == 2039].index.tolist()[-1]
                p3_s = df.YY[df.YY == 2050].index.tolist()[0]
                p3_e = df.YY[df.YY == 2069].index.tolist()[-1]
                p4_s = df.YY[df.YY == 2080].index.tolist()[0]
                p4_e = df.YY[df.YY == 2099].index.tolist()[-1]        
        
                if outputType == 'DESAL':
                    if pars.loc[WP,'DESAL'] == -999:
                        value = 0
                    else:
                        value = pars.loc[WP,'DESAL']
                    ave_p1 = value
                    ave_p2 = value
                    ave_p3 = value
                    ave_p4 = value
        
                elif outputType == 'GWT_storage':
                    ave_p1 = sum(df[outputType][0:p1])/len(df[outputType][0:p1])
                    ave_p2 = sum(df[outputType][p2_s:p2_e])/len(df[outputType][p2_s:p2_e])
                    ave_p3 = sum(df[outputType][p3_s:p3_e])/len(df[outputType][p3_s:p3_e])
                    ave_p4 = sum(df[outputType][p4_s:p4_e])/len(df[outputType][p4_s:p4_e])
                    
                    ave_p1 = 1000 + (ave_p1/(pars.loc[WP,'AREA_WP']*1e6))
                    ave_p2 = 1000 + (ave_p2/(pars.loc[WP,'AREA_WP']*1e6))
                    ave_p3 = 1000 + (ave_p3/(pars.loc[WP,'AREA_WP']*1e6))
                    ave_p4 = 1000 + (ave_p4/(pars.loc[WP,'AREA_WP']*1e6))
                
                else:
                    ave_p1 = sum(df[outputType][0:p1])/(p1/12)
                    ave_p1 = ave_p1/(pars.loc[WP,'AREA_WP']*1000)
                    ave_p2 = sum(df[outputType][p2_s:p2_e])/((p2_e-p2_s)/12)
                    ave_p2 = ave_p2/(pars.loc[WP,'AREA_WP']*1000)
                    ave_p3 = sum(df[outputType][p3_s:p3_e])/((p3_e-p3_s)/12)
                    ave_p3 = ave_p3/(pars.loc[WP,'AREA_WP']*1000)
                    ave_p4 = sum(df[outputType][p4_s:p4_e])/((p4_e-p4_s)/12)
                    ave_p4 = ave_p4/(pars.loc[WP,'AREA_WP']*1000)
                    
                OUT = pd.Series([ave_p1,ave_p2,ave_p3,ave_p4])          
                
                shp_csv[WP] = OUT
                
        shp_csv = shp_csv.T
        shp_csv.index.names = ['WatProvID']
        shp_csv.columns = ['Base','P1','P2','P3']
        
        shp_csv.to_csv(pathOUT+'All_total_'+outputType+'.csv')
#    return shp_csv

def availability_index(index_min,index_max,pop_min,pop_max,pop_dens):
    
    index_diff = index_max - index_min
    pop_diff = pop_max - pop_min
    
    index = index_diff * ((pop_dens - pop_min)/pop_diff) + index_min
    
    index = max(index, index_min)
    index = min(index, index_max)    
    
    return index

def ReadTSS(FName, ID, StartYY, EndYY):
    try:
        FName = FName
        tss = np.load(FName)
    except Exception, e:
        print >> sys.stderr, 'Exception: %s' % str(e)
        sys.exit(1)
    #print ('     Reading TSS :  %s ' %(FName))
#    logging.info (' >Reading TSS (rows, col):  %s %d %d' %(FName, int(tss.shape[0]), int(tss.shape[1])))
#    logging.info ('               FirstYear : %d' %(tss[3, 0]))
#    logging.info ('               LastYear  : %d' %(tss[int(tss.shape[0])-1, 0]))

    #extract the time series data for 'ID' from the tss array AND for the years
    IDs = tss[0,4:]                                           # Retrieve top row from file, except first 4 cols, these are placeholders
    colIdx = 4 + np.searchsorted(IDs, int(ID))                # Find right column, add 4 for the first 4 placeholder columns (YYYY, MM, DD, DD)
    YY  = tss[3:, 0]                                          # Retrive the column containing the year values, except the first 3 rows, these are placeholders CONTAINING WHAT?
    YYstartID = 3 + np.searchsorted(YY, StartYY)              # Find the right starting row, add 3 for the placeholder rows
    YYendID   = YYstartID + ((EndYY - StartYY + 1) * 12)      # Calculate the number of months inbetween

    Col = tss[YYstartID:YYendID , colIdx]
#    logging.info (' >       ==> Finished')
    return Col

    
    
if __name__ == '__main__':
    SCENs = [['RCP_2.6','SSP1'],['RCP_8.5','SSP5']]
    ADAPTs = ['Adpt_0','Adpt_1','Adpt_2','Adpt_3']
    ADAPTs = ['Adpt_0','Adpt_2']
    for scen in SCENs:
        for Adapt in ADAPTs:
            pathIN = r'C:\Users\Joost\Dropbox_offline\Test'
            pathIN += '\\' + Adapt + '\\'
            pathOUT = pathIN + scen[0] + '_' + scen[1] + '\\'
            
            foo = create_shp_csv(pathIN,scen,pathOUT)