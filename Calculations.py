from __future__ import division
import sys
import pandas as pd
import numpy as np

def WatCAM(PARAM, INPUT, demand_types):


    # %% PREPARE OUTPUT DATAFRAME
    
    # Create empty DataFrame
    OUTPUT = pd.DataFrame()
    # Create list with required column names
    OUTPUT_columns = ['YY','MM','FLO_internal','FLO_external','FLO_total','FLO_ava',
                      'TOTAL_ava','RES_inflow','GWT_inflow','FLO_extracted','RES_extracted',
                      'GWT_extracted','FLO_out','RES_storage','GWT_storage']
    
    # Loop through each demand type, and assign name to it
    for typ in demand_types:
        OUTPUT_columns += ['GROSS_dem_'+typ]
    OUTPUT_columns += ['GROSS_dem_tot']
    # Same for Actual withdrawn water    
    for typ in demand_types:
        OUTPUT_columns += ['ACTUAL_withdrawal_'+typ]
    # Same for delivered water
    for typ in demand_types:
        OUTPUT_columns += ['DELIVERED_water_'+typ]
    OUTPUT_columns += ['DELIVERED_tot']
    # Same for unmnet names
    for typ in demand_types:
        OUTPUT_columns += ['UNMET_'+typ]
    OUTPUT_columns += ['UNMET_tot']  
    # Same for consumed
    for typ in demand_types:
        OUTPUT_columns += ['CONSUMED_'+typ]
    OUTPUT_columns += ['CONSUMED_tot']    
    # Same for return flow
    for typ in demand_types:
        OUTPUT_columns += ['RETURN_'+typ]
    OUTPUT_columns += ['RETURN_tot']
    
    # Add the balance in the final position
    OUTPUT_columns += ['BAL']
    
    # Add columns to DataFrame, and copy them to the headers
    OUTPUT = OUTPUT.append(OUTPUT_columns).T  
    OUTPUT.columns = list(OUTPUT.loc[0,])       

        
    # %% EXTEND INPUT FRAME WITH STATIC VARIABLES    
    
    # Calculate the internal generated flow
    INPUT['FLO_internal'] = INPUT['FLO_internal_org'] * float(PARAM['Calibration'])   
    
    # Calculate the externally generated flow
    if float(PARAM['Ext_User']) == 0:
        INPUT['FLO_external'] = INPUT['FLO_external_org']
    else:
        INPUT['FLO_external'] = INPUT['FLO_pristine'] * float(PARAM['Ext_User'])
        
    # Calculate the total generated flow
    INPUT['FLO_total'] = INPUT['FLO_internal'] + INPUT['FLO_external'] + \
                        max(0,float(PARAM['DESAL']))/12 * 1e6
    
    # Calculate the capacity of the reservoir
    INPUT['RES_capacity'] = INPUT['RES_capacity_org'] + (float(PARAM['RES_extra']) * 1e6)
       
    # Calculate the domestic and industry demands, based on demand fractions (to reduced/increase by a percentage in a adaptation scen)
    INPUT['DOM_demand'] = INPUT['DOM_demand_org'] * float(PARAM['URB_DEM'])
    INPUT['IND_demand'] = INPUT['IND_demand_org'] * float(PARAM['IND_DEM'])  
    
    # Calculate the irrigated area fraction, based on the original area and a fraction
    INPUT['IRR_area'] = INPUT['IRR_area_org'] * float(PARAM['IRR_AREA'])
    
    # Calculated the environmental demand
    INPUT['ENV_demand'] = INPUT['FLO_pristine'] * float(PARAM['ENV_FRAC'])
    
    # Calculate the downstream demand
    if float(PARAM['DWN_DEM']) == 0:
        INPUT['DWN_demand'] = INPUT['DWN_demand_org']
    else:
        INPUT['DWN_demand'] = INPUT['FLO_pristine'] * float(PARAM['DWN_DEM'])    

    # %% NET DEMANDS

    DEMAND = {}

    DEMAND['DOM_net'] = INPUT['Population'] * (INPUT['DOM_demand']/1e3) * 30.5
    DEMAND['IND_net'] = INPUT['IND_demand']
    if float(PARAM['IRR_COR']) == 0:
        DEMAND['IRR_net'] = INPUT['IRR_area'] * (INPUT['ET_ref']/1e3)
    else:
        DEMAND['IRR_net'] = (INPUT['IRR_area'] * (INPUT['ET_ref']/1e3)) / float(PARAM['IRR_COR'])
    DEMAND['ENV_net'] = INPUT['ENV_demand']
    DEMAND['DWN_net'] = INPUT['DWN_demand']
    
    # len(INPUT['FLO_pristine']) is equal to the number of months within the required period
    for i in range(len(INPUT['FLO_pristine'])):

        # %% AVAILABLE WATER        
        
        #-Calculate the amount of storage available in the first month
        if i == 0:
            RES_storage_new = float(INPUT['RES_capacity'][i]) * float(PARAM['RES_INIT'])
            GWT_storage_new = 0 # Omit the absolute storage values, now only relative changes

        # Update the current storage values with the values of the previous run
        RES_storage = RES_storage_new
        GWT_storage = GWT_storage_new
        
        # Calculate the groundwater infiltration 
        GWT_inflow = float(INPUT['GW_recharge'][i]) * 1e9 * float(PARAM['GWT_RECH']) #1e9 because GW_recharge is in km3, correction factor for recharge  
                
        # Calculate the amount of illegal extracted groundwater
        INFORMAL_sup = ( float(INPUT['FLO_internal'][i]) - GWT_inflow) * float(PARAM['INFORMAL'])
        
        # Calculate the POTENTIAL reservoir outflow
        RES_ava = RES_storage * float(PARAM['RES_MAX'])
        
        # Calculate the POTENTIAL groundwater outflow
        GWT_ava = (float(INPUT['Average_rech'][i]) * float(PARAM['GWT_RECH'])) * float(PARAM['GWT_MAX']) # Include the same correction factor for the recharge
        
        # Calculate the total available surface water
        FLO_ava = float(INPUT['FLO_total'][i]) - GWT_inflow - INFORMAL_sup
        
        # Calculate the total POTENTIALLY available water
        TOTAL_ava = FLO_ava + RES_ava + GWT_ava
        
        
        # %% DEMAND AND SUPPLY        
        #-Create empty data structures, to store data in
        dem_sup = {}       
        list_of_demands = []
        list_of_priorities = []
        list_of_REQs = []        
        #-Loop through all demand types
        for typ in demand_types:
            #-Environment and downstream demand sector do not have consumed and reuse fractions
            if typ == 'ENV' or typ == 'DWN':
                dem_sup['REQ_withdrawal_'+typ] = float(DEMAND[typ+'_net'][i])
            #-All other types do, and need to be corrected for
            else:
                dem_sup['REQ_withdrawal_'+typ] = required_withdrawal(float(DEMAND[typ+'_net'][i]),float(PARAM[typ+'_CONS_F']),float(PARAM[typ+'_REU']))
            list_of_REQs += [dem_sup['REQ_withdrawal_'+typ]]
            list_of_priorities += [float(PARAM[typ+'_PRI'])]      
        #-Total required withdrawan
        REQ_withdrawal_TOT = sum(list_of_REQs)
        #-Determine the possible actual withdrawal (see equation below)
        ACTUAL_withdrawn = supply_demand(TOTAL_ava, list_of_REQs,list_of_priorities)
        #-Write the results to a DataFrame
        for typ in demand_types:
            dem_sup['ACTUAL_withdrawal_'+typ] = ACTUAL_withdrawn[demand_types.index(typ)]
        #-Determine total values
        ACTUAL_withdrawn_TOT = sum(ACTUAL_withdrawn)
        
        GROSS_dem_tot = 0
        CONSUMED_tot = 0
        DELIVERED_tot = 0
        RETURN_tot = 0
        UNMET_tot = 0
        #-Store data and determine total volumes, for reporting later on
        for typ in demand_types:
            dem_sup['GROSS_dem_'+typ] = float(DEMAND[typ+'_net'][i])
            if typ == 'DWN':
                dem_sup['DELIVERED_water_'+typ] = ACTUAL_withdrawn[demand_types.index(typ)]
                dem_sup['CONSUMED_'+typ] = dem_sup['DELIVERED_water_'+typ] * 0
                dem_sup['RETURN_'+typ] = dem_sup['DELIVERED_water_'+typ] - dem_sup['CONSUMED_'+typ]
            elif typ == 'ENV':
                dem_sup['DELIVERED_water_'+typ] = ACTUAL_withdrawn[demand_types.index(typ)]
                dem_sup['CONSUMED_'+typ] = dem_sup['DELIVERED_water_'+typ] * float(PARAM[typ+'_USE'])
                dem_sup['RETURN_'+typ] = dem_sup['DELIVERED_water_'+typ] - dem_sup['CONSUMED_'+typ]
            else:
                withdrawn = ACTUAL_withdrawn[demand_types.index(typ)]      
                deli,cons,retu = actual_delivered(withdrawn,float(PARAM[typ+'_CONS_F']),float(PARAM[typ+'_REU']))
                dem_sup['DELIVERED_water_'+typ] = deli
                dem_sup['CONSUMED_'+typ] = cons
                dem_sup['RETURN_'+typ] = retu
            dem_sup['UNMET_'+typ] = max(0, dem_sup['GROSS_dem_'+typ] - dem_sup['DELIVERED_water_'+typ])
            
            GROSS_dem_tot += dem_sup['GROSS_dem_'+typ]
            DELIVERED_tot += dem_sup['DELIVERED_water_'+typ]    
            CONSUMED_tot += dem_sup['CONSUMED_'+typ]
            RETURN_tot += dem_sup['RETURN_'+typ]
            UNMET_tot += dem_sup['UNMET_'+typ]
            

        # %% PERFORM FINAL UPDATE CALCULATIONS
    
        # Calculate extracted surface water
        FLO_extracted = min(ACTUAL_withdrawn_TOT, FLO_ava)
        # Extracted reservoir water
        RES_extracted = min(ACTUAL_withdrawn_TOT - FLO_extracted, RES_ava)
        # Extracted groundwater
        GWT_extracted = min(ACTUAL_withdrawn_TOT - FLO_extracted - RES_extracted, GWT_ava)
        # Reservoir inflow
        RES_inflow = min(FLO_ava - FLO_extracted, float(INPUT['RES_capacity'][i]) - RES_storage)
        
        # New reservoir storage
        RES_storage_new = RES_storage - RES_extracted + RES_inflow
        GWT_storage_new = GWT_storage - GWT_extracted + GWT_inflow
        
        # Possible groundwater extraction
        if GWT_storage_new > 0:
            GWT_outflow = GWT_storage_new
        else:
            GWT_outflow = 0
        GWT_storage_new = GWT_storage_new - GWT_outflow                
        
        # Water leaving the water province
        FLO_out = FLO_ava - FLO_extracted - RES_inflow + RETURN_tot + GWT_outflow
        
        # Balance
        BAL = float(INPUT['FLO_total'][i]) - (CONSUMED_tot + FLO_out) - (RES_storage_new - RES_storage) - (GWT_storage_new - GWT_storage)
   
        # %% WRITE VALUES TO OUTPUT DATAFRAME  
        
        toOutput = []
        for var in OUTPUT_columns:
            if var in INPUT:
                toOutput += [float(INPUT[var][i])]
            elif var in dem_sup:
                toOutput += [dem_sup[var]]
            elif var in locals():
                toOutput += [locals().get(var)]
            else:
                print var + ' is not known as a variable, please change OUTPUT_columns'
                sys.exit(1)

        if i == 0:
            npOutput = np.copy(toOutput)
        else:
            npOutput = np.vstack((npOutput,toOutput))

    OUTPUT = pd.DataFrame(npOutput, columns= OUTPUT_columns)
    return OUTPUT

def required_withdrawal(gross_demand,consumed_f,reuse_f):
    '''
    Calculate the required withdrawal of water from the watersupply, ginven the
    gross demand, consumed and reuse fractions.
    
    Input
    -----
    gross_demand: float
        The gross demand for a given demand type
    consumed_f: float
        The fraction of the gross demand that is consumed
    reuse_f: float
        Fraction of the non-consumed water that is being reused
        
    Output
    -----
    withdrawal_req: float
        The amount of water is required to be withdrawn from the water supply
        in order to meet the gross demand
    '''
    consumed = gross_demand * consumed_f
    reuse = (gross_demand - consumed) * reuse_f     
    
    withdrawal_req = gross_demand - reuse
    
    return withdrawal_req
    
def actual_delivered(actual_withdrawal,consumed_f,reuse_f):
    '''
    Calculate the actual water deliverd, consumed and returned based on the
    water that is available to be withdrawn
    
    Input
    -----
    actual_withdrawal: float
        Amount of water that is able to be extracted fromt the water supply for
        a given demand type
    consumed_f: float
        The fraction of water that is consumed
    reuse_f: float
        Fraction of the non-consumed water that is being reused
    
    Output
    -----
    water_delivered: float
        Actual water delivered to the demand site, given the actual withdrawal
    consumed: float
        Water that is consumed by the demand site
    return_flow: float
        Water that is not consumed and not reused, will be returned to the river
        as streamflow
    '''   
    
    water_delivered = actual_withdrawal / ((consumed_f - 1) * reuse_f + 1)
    consumed = water_delivered * consumed_f
    
    return_flow = actual_withdrawal - consumed
    
    return water_delivered, consumed, return_flow


def supply_demand(available, demands, priorities):
    '''
    The function distributes the available water between the different demand
    types, according to their priorities.
    
    Input
    -----
    available: float
        Total available water
    demands: list of floats
        List containing the gross demands for each demand type (number of demands 
        is accepted)
    priorities: list of floats/integers
        List containing the priorities for each demand type. It is important that 
        the order of priorities is equal to the order in which the demands are
        presented
        
    Output
    -----
    total_supply: list of floats
        List with the actual supply for each demand type. This list is in the
        same order as the demands list from the input
    '''
    
    if len(demands) != len(priorities):
        raise ValueError('Length demands and piorities unequal')
    
    total_supply = [0] * len(demands)
    
    def check(ava, tot):
        '''
        This function checks whether the available water and the total demand
        are already met (keeping a certain amount of precision in mind, which is
        defined in this function)
        
        Input
        -----
        ava: float
            Total available water
        tot: float
            Sum of the demands that still need to be met
            
        Output
        -----
        cont: boolean
            Returns True when both the demands are not yet met, and there is still
            water available. Returns False when either: ava <= precision or tot <=
            precision.
        '''
        precision = 1e-10
        if ava <= precision:
            cont = False
        elif tot <= precision:
            cont = False
        else:
            cont = True
        return cont

    Continue = check(available, sum(demands))    
    
    while Continue:    
        
        PRI_fractions = 0
        ADJ = []
        for i in range(len(demands)):
            PRI_fractions += demands[i]/priorities[i]
            if demands[i] > 0:
                ADJ += [priorities[i]]
        
        PRI_total = available/PRI_fractions
        ADJ += [PRI_total]
        ADJ = min(ADJ)
    
        supply = []    
        for i in range(len(demands)):
            supply += [ADJ * (demands[i]/priorities[i])]
            total_supply[i] += supply[i]
            demands[i] = demands[i] - supply[i]
        
        available = available - sum(supply)
        
        Continue = check(available, sum(demands))

    return total_supply