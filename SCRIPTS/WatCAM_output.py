import pandas as pd
import p_Time_series as p1
import p_Box_plot as p2
import matplotlib.pyplot as plt


# %% PLOTTING PARAMETERS
WP = 1400
OUT_folder = 'Segura_ADPT_betterPars'

scen = ['RCP_2.6','SSP1']
scen = ['RCP_8.5','SSP3']
Adpt = 'Adpt_0'

width = 0.6

RCP = scen[0]
SSP = scen[1]

OUT_file = 'c:/Users/Joost/Dropbox/W2I_Demo/MODEL/WatCam2016/WatCAM_v4/Output/'+OUT_folder+'/'+Adpt+'/'+str(WP)+'_'+RCP+'_'+SSP+'.csv'

pos = [0   ,47  ,228 ,528 ,828 ,1128]
yrs = [2006,2010,2025,2050,2075,2100]

# %% SETTING UP THE DATA
df = pd.DataFrame.from_csv(OUT_file,index_col=False)

df['YY'] = df.YY.map(int)
df['MM'] = df.MM.map(int)

df['Period'] = df.YY.map(str) + "_" + df.MM.map(str)

# Replace all small values with a zero
for typ in ['DOM','IND','IRR','ENV','DWN','tot']:
    df['UNMET_'+typ][df['UNMET_'+typ]<0.1] = 0

x = range(len(df['YY']))

for col in df.columns:
    if col not in ['YY','MM','Period','BAL']:
        df[col] /= 1000000


# %% PLOTTING THE DATA

# Time series of available and demand
p1.AVA_DEM_SUP(WP,RCP,SSP,x,df,pos,yrs)

# Time series of demand and supply values
p1.SUP_per_DEM(WP,RCP,SSP,x,df,pos,yrs)

# Boxplot of the water balcne
p2.box_WBAL(WP,RCP,SSP,df,width)
plt.grid(axis='y')

# Clear figure to prevent strange things happening
try:
    fig.clear()
except NameError:
    pass
# Plot the gross and unmet demands as boxplots
fig = p2.box_DEM(WP,RCP,SSP,df,width)
plt.grid(axis='y')

# %% AVERAGES OF DATA
p2_s = df.YY[df.YY == 2020].index.tolist()[0]
p2_e = df.YY[df.YY == 2039].index.tolist()[-1]
p3_s = df.YY[df.YY == 2050].index.tolist()[0]
p3_e = df.YY[df.YY == 2069].index.tolist()[-1]
p4_s = df.YY[df.YY == 2080].index.tolist()[0]
p4_e = df.YY[df.YY == 2099].index.tolist()[-1]

AVERAGE = pd.DataFrame()

for typ in list(df):
    if typ not in ['YY','MM','Period','BAL']:
        AVERAGE[typ] = pd.Series([sum(df[typ][0:120])/10,sum(df[typ][p2_s:p2_e])/19,
                              sum(df[typ][p3_s:p3_e])/19,sum(df[typ][p4_s:p4_e])/19])

AVERAGE.to_clipboard(excel=True)


# %% GROUNDWATER STORAGE AND EXTRACTION PLOT

#fig = plt.figure(str(WP)+'_'+RCP+'_'+SSP+'_GWT_storage',dpi=110,figsize=plt.figaspect(0.5))
#fig.clear()
#
#ax1 = fig.add_subplot(111)
#ax1.plot(df.GWT_storage,'b',lw=1.5,label='Groundwater storage')
#ax1.set_ylim(ymin=0)
#
#ax2 = ax1.twinx()
#ax2.plot(df.GWT_extracted,'g',lw=1.5,label='Groundwater extraction')
#ax2.set_ylim(ymin=0,ymax=100)
#
#plt.xlim(xmax=len(df.YY))
#plt.xticks(pos,yrs)
#
#ax1.set_ylabel(r'Storage $\mathregular{(x10^6\ m^3)}$', color='b')
#ax2.set_ylabel(r'Extraction rate $\mathregular{(x10^6\ m^3month^{-1})}$', color='g')
#
#plt.tight_layout()
#plt.show()





# %% OLD

#col_SUP = ['#33a02c','#b2df8a','#253494','#2c7fb8','#41b6c4','#a1dab4']
#
#col_SUP = ['#c7eae5','#5ab4ac','#01665e']
#
#col_UNM = ['#8c510a','#d8b365','#f6e8c3']
#label1 = ['SUP_dom','SUP_ind','SUP_irr']
#label2 = ['UNM_dom','UNM_ind','UNM_irr']
#col_UNM.reverse()
#
#SUP = []
#UNM = []
#
#for typ in ['DOM','IND','IRR']:
##    SUP += [list(np.cumsum(df['SUP_'+typ]))]
#    SUP += [list((df['DELIVERED_water_'+typ]))]
##    UNM += [list(np.cumsum(df['UNMET_'+typ]*-1))]
#    UNM += [list((df['UNMET_'+typ]*-1))]
#
#TOT = []
#for typ in ['DOM','IND','IRR']:
#    TOT += [list(df['DELIVERED_water_'+typ])]
#    TOT += [list(df['UNMET_'+typ])]
#
#
#fig2 = plt.figure('SUP_per_DEM',dpi=110, facecolor='white',figsize=plt.figaspect(0.5))
#
#sp1 = plt.stackplot(x, SUP, colors = col_SUP+col_UNM)
#sp2 = plt.stackplot(x, UNM, colors = col_UNM)
#
#proxy1 = [mpl.patches.Rectangle((0,0), 0,0, facecolor=pol.get_facecolor()[0]) for pol in sp1]
#proxy2 = [mpl.patches.Rectangle((0,0), 0,0, facecolor=pol.get_facecolor()[0]) for pol in sp2]
#
#plt.legend(proxy1 + proxy2, label1+label2,loc=2,ncol = len(label1+label2))
#
#ax=plt.gca()
#
## Hide the right and top spines
#ax.spines['right'].set_visible(False)
#ax.spines['top'].set_visible(False)
#ax.yaxis.set_ticks_position('left')
#ax.xaxis.set_ticks_position('bottom')
#
#plt.tight_layout()









