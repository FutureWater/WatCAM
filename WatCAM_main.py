import os,shutil, time
import numpy as np
from ReadFiles import ReadParamFile, ReadWatProvIDs, ReadInputFiles
from Calculations import WatCAM
from ExternalFlow import ReadWPDown, Add_Headflow

#%% USER OPTIONS
#-Select basin
BAS = [ 'World',] #, 'World', 'Africa'] #['Rhine', 'Mekong', 'Amazone','Nile', 'Africa'] 'Amu Darya', 'Mekong', 'Amazone', 'Amur', 'Chao Phraya', 'Congo', 'Danube', 'Indus', 'Krishna', 'Mississippi', 'Nile', 'Orange', 'Orinoco', 'Po', 'Rhine', 'Syr Darya', 'Yangtze'
#-Select adaptation strategies
RUNS = ['Adpt_0',]#,'Adpt_1', 'Adpt_2', 'Adpt_3', 'Adpt_4', 'Adpt_5','Adpt_6','Adpt_7'] # ['HIST_GEN35'] #, 'Adpt_1', 'Adpt_2', 'Adpt_3', 'Adpt_4', 'Adpt_5','Adpt_6'] # , 'Adpt_0', 'Adpt_2', 'Adpt_3', 'Adpt_4', 'Adpt_5', 'Adpt_6'] #'Adpt_0', 'Adpt_1', 'Adpt_2', 'Adpt_3', 'Adpt_4', 'Adpt_5',, 'Adpt_7' 'HIST_GEN0', 'HIST_GEN1', 'HIST_GEN2', 'HIST_GEN3', 'HIST_GEN4', 'HIST_GEN5', 'HIST_GEN6', 'HIST_GEN7', 'HIST_GEN8', 'HIST_GEN9', 'HIST_GEN10', 'HIST_GEN11','HIST_GEN12'
#-Select RCP+SSP scenario combination(s)
RCPSSP = [['RCP_2.6','SSP1'],
          ['RCP_2.6','SSP2'],
          ['RCP_2.6','SSP3'],
          ['RCP_2.6','SSP4'],
          ['RCP_2.6','SSP5'],
          ['RCP_4.5','SSP1'],
          ['RCP_4.5','SSP2'],
          ['RCP_4.5','SSP3'],
          ['RCP_4.5','SSP4'],
          ['RCP_4.5','SSP5'],
          ['RCP_6.0','SSP1'],
          ['RCP_6.0','SSP2'],
          ['RCP_6.0','SSP3'],
          ['RCP_6.0','SSP4'],
          ['RCP_6.0','SSP5'],
          ['RCP_8.5','SSP1'],
          ['RCP_8.5','SSP2'],
          ['RCP_8.5','SSP3'],
          ['RCP_8.5','SSP4'],
          ['RCP_8.5','SSP5']]
#-Select future or historic run (only future relevant, historic contains errors)
INGEN = "General_FUT"
#-Name of the output folder
Experiment = "Reference"
#-Directory of the model
dirModel = r'C:\Software\Repository\WatCAM'
#-Start and end years
StartYY = 2006
EndYY = 2099
#-Demand types can be changed; not necessary
demand_types = ['DOM','IND','IRR','ENV','DWN']


#%% CALLING THE MODEL
start_time = time.time()
#-Loop through all basin options
for basin in BAS:
    
    # %% Read the file containing data avout the required Water Provinces
    file_WP = os.path.join(dirModel,'Input','WatProv','WatProv_' + basin + '.csv')
    order_IDs = ReadWatProvIDs(file_WP)
   
    # %% Check wheter only one WP is ran, or more
    if len(order_IDs) == 1:
        SingleWP = True
    else:
        SingleWP = False
    #-Loop through adaptation options    
    for RUN in RUNS:
        #-Loop through scenario combinations
        for scen in RCPSSP:
            
            # %% Set the right folder to read the input files from
            dir_INPUT = os.path.join(dirModel,'Input')
            dir_RCP = scen[0]
            dir_SSP = scen[1]
            dir_GEN = INGEN 
            
            if SingleWP:
                shutil.copyfile(os.path.join(dir_INPUT, dir_GEN,'ExtFlowBAU.tss.npy'), os.path.join(dir_INPUT, dir_RCP, 'ExtFlow.tss.npy'))     # headflows from BAU (! this should finally be taken from run of same future scenario)
            else:
                shutil.copyfile(os.path.join(dir_INPUT, dir_GEN, 'ZERO.tss.npy'), os.path.join(dir_INPUT, dir_RCP, 'ExtFlow.tss.npy'))     # headflows are intially zero
            
            #-Loop through all water provinces
            for ID in order_IDs:

                # Select only the WP ID
                ID = ID[1]

                print 'Running ' + scen[0] + '_' + scen[1] + ' ' + str(ID) + ' ' + RUN         
                
                # %% Read the parameter file
                file_PAR = os.path.join(dirModel, 'Param', RUN + '.csv')
                PARAM = ReadParamFile(file_PAR, ID)   
                
                # %% Read in the input files
                INPUT = ReadInputFiles(dir_INPUT, dir_RCP, dir_SSP, dir_GEN, ID, StartYY, EndYY)
                
                # %% Run the WatCAM model
                OUTPUT = WatCAM(PARAM, INPUT, demand_types)
                
                # %% Check whether the output folder already exists
                dirOutput = os.path.join(dirModel, 'Output', Experiment, RUN, scen[0] + '_' + scen[1])# +'/'
                if not os.path.exists(dirOutput):
                    os.makedirs(dirOutput)
                OUTPUT.to_csv(os.path.join(dirOutput, 'WP_{:04d}'.format(ID) + '.csv'),index=False)
                
                #-Extract downstream WP and fractions
                DOWN, FRAC = ReadWPDown(file_WP, ID)
                #-Extract flow out of the current WP
                Qout = np.array(list(OUTPUT['FLO_out']))
                #-Loop through all downstream WPs
                for i in range(len(DOWN)):
                    # Do not replace the external flow when the downstream WP is equal to the WP itself
                    if DOWN[i] != ID:
                        file_FLO_EXT = os.path.join(dir_INPUT, dir_RCP, 'ExtFlow.tss')
                        Add_Headflow(file_FLO_EXT, DOWN[i], Qout, FRAC[i], StartYY, EndYY)                


elapsed_time = time.time() - start_time
print '>>> WatCAM finished, elapsed time is %.2f seconds' % elapsed_time
