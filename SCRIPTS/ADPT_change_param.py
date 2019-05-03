import pandas as pd

#%% Read original file
paramLoc = r'c:\Users\Joost\Dropbox\W2I_Demo\MODEL\WatCam2016\WatCAM_paper\Param3.02'+'\\'
header = pd.read_csv(paramLoc + 'Adpt_0.csv',header=None)
header = header.loc[0:1,]
header.columns = header.loc[1,]

Adpt_0 = pd.read_csv(paramLoc+'Adpt_0.csv',header=1)
#%% Adapt_1 Imp.Arg.
Adpt_1 = Adpt_0.copy()

IRR_CONS_F_new = (1 - Adpt_0.IRR_CONS_F) * 0.4 + Adpt_0.IRR_CONS_F

ratio = Adpt_0.IRR_CONS_F / IRR_CONS_F_new

IRR_AREA_new = pd.Series()
for index, row in ratio.iteritems():
    if ratio[index] == 0:
        tmp = pd.Series([Adpt_0.IRR_AREA[index]],index=[index])
        IRR_AREA_new = IRR_AREA_new.append(tmp)
    else:
        tmp = pd.Series([Adpt_0.IRR_AREA[index]*ratio[index]],index=[index])
        IRR_AREA_new = IRR_AREA_new.append(tmp)

Adpt_1.IRR_CONS_F = IRR_CONS_F_new
Adpt_1.IRR_AREA = IRR_AREA_new

#%% Adapt_2 Inc.Sup.
Adpt_2 = Adpt_1.copy()

# Expand reservoir by 1000MCM
Adpt_2.RES_extra = Adpt_1.RES_extra + 1000

# Increase reuse irr from 20 -> 60 %
IRR_REU_new = (1 - Adpt_1.IRR_REU) * 0.5 + Adpt_1.IRR_REU
Adpt_2.IRR_REU = IRR_REU_new

# Increase reuse dom+ind from 50 -> 80%
DOM_REU_new = (1 - Adpt_1.DOM_REU) * 0.6 + Adpt_1.DOM_REU
IND_REU_new = (1 - Adpt_1.IND_REU) * 0.6 + Adpt_1.IND_REU
Adpt_2.DOM_REU = DOM_REU_new
Adpt_2.IND_REU = IND_REU_new

# Add DESAL of 1000 MCM/year
Adpt_2.DESAL[Adpt_1.DESAL >= 0] = Adpt_1.DESAL + 1000



#%% Adaot_3 Red.Dem.
Adpt_3 = Adpt_2.copy()

# Reduce dom+ind demand by 15%
Adpt_3.URB_DEM = 0.85
Adpt_3.IND_DEM = 0.85



#%% Write each file to disk


Adpt_1 = pd.concat([header,Adpt_1])
Adpt_1.to_csv(paramLoc+'Adpt_1.csv',header=False,index=False)
# Save new file
Adpt_2 = pd.concat([header,Adpt_2])
Adpt_2.to_csv(paramLoc+'Adpt_2.csv',header=False,index=False)
# Save new file
Adpt_3 = pd.concat([header,Adpt_3])
Adpt_3.to_csv(paramLoc+'Adpt_3.csv',header=False,index=False)

#print '\n\nAdd first row manually from Adpt_0 file \n\n'