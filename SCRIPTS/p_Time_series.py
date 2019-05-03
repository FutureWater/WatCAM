import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


###############################################################################
############################# TIME SERIES #####################################
###############################################################################

def AVA_DEM_SUP(WP,RCP,SSP,x,df,pos,yrs):

    fig = plt.figure(str(WP)+'_'+RCP+'_'+SSP+'_AVA_DEM_SUP', dpi=110,facecolor='white',figsize=plt.figaspect(0.5))

    fig.clear()    
    
#    plt.plot(x,df['FLO_internal'],c='#5ab4ac',label='Internal flow',lw=1.5)
    plt.plot(x,df['TOTAL_ava'],c='#01665e',label='Total flow',lw=1.5)#01665e
    plt.plot(x,df['GROSS_dem_tot'], c='#d8b365',label='Gross demand',lw=1.5)
    plt.plot(x,df['DELIVERED_tot'],c='#8c510a',label='Total delivered',lw=1.5)
    
    ax = plt.gca()
    
    ax.fill_between(x, df['DELIVERED_tot'], df['GROSS_dem_tot'], where=df['GROSS_dem_tot'] >= df['DELIVERED_tot'], 
                    facecolor='#d8b365', alpha=.6, interpolate=True,label='Unmet demand')
    
    plt.legend(loc=0)
    plt.xlim(xmax=len(df.YY))
    plt.xticks(pos,yrs)
    #ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.ylabel(r'Amount of water ($\mathregular{x10^6\ m^3}$)')
    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    
    plt.suptitle('WP: '+str(WP)+' -- '+RCP+' '+SSP,fontsize=16)
    
#    plt.tight_layout()
#    bx1.subplots_adjust(bottom=0.15,top=0.88)
    plt.tight_layout()


def SUP_per_DEM(WP,RCP,SSP,x,df,pos,yrs):
    ################################################################################
    ################################################################################
    ################################################################################
    
    fig = plt.figure(str(WP)+'_'+RCP+'_'+SSP+'_SUP_per_DEM',dpi=110, facecolor='white',figsize=plt.figaspect(0.5))

    fig.clear()    
    
    TOT = []
    for typ in ['DOM','IND','IRR']:
        TOT += [list(df['DELIVERED_water_'+typ])]
        TOT += [list(df['UNMET_'+typ])]
    
    col_TOT = ['#01665e','#5ab4ac','#8c510a','#d8b365','#587905','#8CCC31']
    label = ['DELI_dom','UNM_dom','DELI_ind','UNM_ind','DELI_irr','UNM_irr']
    
    sp1 = plt.stackplot(x, TOT, colors = col_TOT)
    
    proxy1 = [mpl.patches.Rectangle((0,0), 0,0, facecolor=pol.get_facecolor()[0]) for pol in sp1]
    
    plt.legend(proxy1, label,loc=2,ncol = len(label))
    plt.xticks(pos,yrs)
    plt.xlim(xmax=len(df.YY))
    ax=plt.gca()
    plt.ylabel(r'Amount of water ($\mathregular{x10^6\ m^3}$)')
    
    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    
    plt.suptitle('WP: '+str(WP)+' -- '+RCP+' '+SSP,fontsize=16)
    
#    plt.tight_layout()
#    bx1.subplots_adjust(bottom=0.15,top=0.88)
    plt.tight_layout()