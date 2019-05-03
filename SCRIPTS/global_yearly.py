from __future__ import division
import pandas as pd
import sys
import numpy as np

def create_shp_csv(pathIN,scen,pathOUT):

    ALLoutputType = ['FLO_internal','FLO_external','FLO_ava','FLO_extracted','RES_extracted','GWT_storage','GWT_inflow','GWT_extracted',
                     'GROSS_dem_DOM','GROSS_dem_IND','GROSS_dem_IRR','GROSS_dem_ENV',
                     'UNMET_DOM','UNMET_IND','UNMET_IRR','UNMET_ENV']

#    ALLoutputType = ['FLO_internal']
    
    
    pars = pd.read_csv(r'c:\Users\Joost\Dropbox\W2I_Demo\MODEL\WatCam2016\Param\NEW_Param\Adpt_0.csv',header=1)
    pars = pars.set_index(pars['WatProvID'])

    allWPs = range(1,1605)
        
    FName = r'c:\Users\Joost\Dropbox\W2I_Demo\MODEL\WatCam2016\Input\NEW\General_FUT\GW_cap.tss.npy'
    GW_cap = np.load(FName)
    GW_cap = pd.DataFrame(data=GW_cap[1:,0:],columns=GW_cap[0,0:])    
    cols = ['YY','D1','D2','D3'] + list(GW_cap.columns[4:])
    GW_cap.columns = cols
    
    RCP = scen[0]
    SSP = scen[1]    
    
    FName = r'c:\Users\Joost\Dropbox\W2I_Demo\MODEL\WatCam2016\Input\NEW\\'+SSP+r'\population.tss.npy'
    POP = np.load(FName)
    POP = pd.DataFrame(data=POP[1:,0:],columns=POP[0,0:])    
    cols = ['YY','D1','D2','D3'] + list(POP.columns[4:])
    POP.columns = cols
    
    df1 = {}    
    df2 = {}
    df3 = {}
    df4 = {}
    
    for outputType in ALLoutputType:
        print outputType        
        for WP in allWPs:       
            
            # For checking purposes later on
            df = 0        
            # Define the filename of the output csv
            FName = pathIN + str(WP) + '_' + RCP + '_' + SSP + '.csv'
            
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
        
                ave_p1 = sum(df[outputType][0:p1])/(p1/12)
                ave_p2 = sum(df[outputType][p2_s:p2_e])/((p2_e-p2_s)/12)
                ave_p3 = sum(df[outputType][p3_s:p3_e])/((p3_e-p3_s)/12)
                ave_p4 = sum(df[outputType][p4_s:p4_e])/((p4_e-p4_s)/12)
                
                if ave_p1 > 1e26:
                    ave_p1 = 0
                if ave_p2 > 1e26:
                    ave_p2 = 0
                if ave_p3 > 1e26:
                    ave_p3 = 0
                if ave_p4 > 1e26:
                    ave_p4 = 0

                try:
                    df1[outputType] += ave_p1
                except:
                    df1[outputType] = ave_p1
                try:
                    df2[outputType] += ave_p2
                except:
                    df2[outputType] = ave_p2
                try:
                    df3[outputType] += ave_p3
                except:
                    df3[outputType] = ave_p3
                try:
                    df4[outputType] += ave_p4
                except:
                    df4[outputType] = ave_p4
                    
    return df1,df2,df3,df4
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
    pathIN = r'c:\Users\Joost\Dropbox\W2I_Demo\MODEL\WatCam2016\WatCAM_v7\Output\Global_FINAL\Adpt_0'
    pathIN += '\\'
    scen = ['RCP_4.5','SSP2']
    pathOUT = r'c:\Users\Joost\Dropbox\W2I_Demo\MODEL\WatCam2016\WatCAM_v7\Output\Global_FINAL'+ '\\'
    
    p1,p2,p3,p4 = create_shp_csv(pathIN,scen,pathOUT)
    
    for key in p1:
        p1[key] = [p1[key]]
    for key in p2:
        p2[key] = [p2[key]]
    for key in p3:
        p3[key] = [p3[key]]
    for key in p4:
        p4[key] = [p4[key]]
    
    
    p1 = pd.DataFrame.from_dict(p1)
    p2 = pd.DataFrame.from_dict(p2)
    p3 = pd.DataFrame.from_dict(p3)
    p4 = pd.DataFrame.from_dict(p4)
    