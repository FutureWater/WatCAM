import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def setBoxColors(bp):  
    for i in range(len(bp['boxes'])):
        
        c = ['#8073ac','#e08214','#b35806','#7f3b08']
        c2 = ['#b6afd0','#f5c38a','#f99339','#CC600D']
        
        plt.setp(bp['boxes'][i], edgecolor=c[i])
        plt.setp(bp['caps'][i+i], color=c[i])
        plt.setp(bp['caps'][i+i+1], color=c[i])
        plt.setp(bp['whiskers'][i+i], color=c[i])
        plt.setp(bp['whiskers'][i+i+1], color=c[i])
        plt.setp(bp['medians'][i], color=c[i])
        bp['boxes'][i].set(facecolor=c2[i])

def box_WBAL(WP,RCP,SSP,df,width):

    p1 = 120
    
    p2_s = df.YY[df.YY == 2020].index.tolist()[0]
    p2_e = df.YY[df.YY == 2039].index.tolist()[-1]
    
    p3_s = df.YY[df.YY == 2050].index.tolist()[0]
    p3_e = df.YY[df.YY == 2069].index.tolist()[-1]
    
    p4_s = df.YY[df.YY == 2080].index.tolist()[0]
    p4_e = df.YY[df.YY == 2099].index.tolist()[-1]

    bx1 = plt.figure(str(WP)+'_'+RCP+'_'+SSP+'_Water_balance',dpi=110,facecolor='white',figsize=plt.figaspect(0.5))
    
    bx1.clear()    
    
    FLO_INT = [df['FLO_internal'][0:p1],df['FLO_internal'][p2_s:p2_e],df['FLO_internal'][p3_s:p3_e],
                df['FLO_internal'][p4_s:p4_e]]
    FLO_EXT = [df['FLO_external'][0:p1],df['FLO_external'][p2_s:p2_e],df['FLO_external'][p3_s:p3_e],
                df['FLO_external'][p4_s:p4_e]]
    DEM_TOT = [df['GROSS_dem_tot'][0:p1],df['GROSS_dem_tot'][p2_s:p2_e],df['GROSS_dem_tot'][p3_s:p3_e],
                df['GROSS_dem_tot'][p4_s:p4_e]]
    UNM_TOT = [df['UNMET_tot'][0:p1],df['UNMET_tot'][p2_s:p2_e],df['UNMET_tot'][p3_s:p3_e],
                df['UNMET_tot'][p4_s:p4_e]]            
    
    bp = plt.boxplot(FLO_INT,positions=[1,2,3,4],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    bp = plt.boxplot(FLO_EXT,positions=[6,7,8,9],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    bp = plt.boxplot(DEM_TOT,positions=[11,12,13,14],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    bp = plt.boxplot(UNM_TOT,positions=[16,17,18,19],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    
    
    plt.xlim(0,20)
    plt.ylim(ymin=-0.1,ymax=1200)
    
    plt.ylabel(r'Amount of water $\mathregular{(x10^6\ m^3month^{-1})}$')
    
    ax = plt.axes()
#    ax.set_yscale('log')
    ax.set_xticklabels(['Internal flow', 'External flow', 'Total demand','Total unmet'])
    ax.set_xticks([2.5, 7.5, 12.5, 17.5])
    
    c = ['#8073ac','#e08214','#b35806','#7f3b08']
    
    h1, = plt.plot([1,1],c=c[0])
    h2, = plt.plot([1,1],c=c[1])
    h3, = plt.plot([1,1],c=c[2])
    h4, = plt.plot([1,1],c=c[3])
    plt.legend((h1,h2,h3,h4),('2006-2015','2020-2039','2050-2069','2080-2099'),
               ncol=4,loc=9,bbox_to_anchor=(0.5,-0.08),frameon=False,fontsize=12.5)
    h1.set_visible(False)
    h2.set_visible(False)
    h3.set_visible(False)
    h4.set_visible(False)
    
    plt.suptitle('WP: '+str(WP)+' -- '+RCP+' '+SSP,fontsize=16)
    
    plt.tight_layout()
    bx1.subplots_adjust(bottom=0.15,top=0.88)
    
    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    
    
    plt.show()

###############################################################################
###################### BOX PLOTS FOR DEMANDS ##################################
###############################################################################

def box_DEM(WP,RCP,SSP,df,width):
    
    p1 = 120
    
    p2_s = df.YY[df.YY == 2020].index.tolist()[0]
    p2_e = df.YY[df.YY == 2039].index.tolist()[-1]
    
    p3_s = df.YY[df.YY == 2050].index.tolist()[0]
    p3_e = df.YY[df.YY == 2069].index.tolist()[-1]
    
    p4_s = df.YY[df.YY == 2080].index.tolist()[0]
    p4_e = df.YY[df.YY == 2099].index.tolist()[-1]
    
    
    DOM_DEM = [df['GROSS_dem_DOM'][0:p1],df['GROSS_dem_DOM'][p2_s:p2_e],df['GROSS_dem_DOM'][p3_s:p3_e],
                df['GROSS_dem_DOM'][p4_s:p4_e]]
    IND_DEM = [df['GROSS_dem_IND'][0:p1],df['GROSS_dem_IND'][p2_s:p2_e],df['GROSS_dem_IND'][p3_s:p3_e],
                df['GROSS_dem_IND'][p4_s:p4_e]]
    IRR_DEM = [df['GROSS_dem_IRR'][0:p1],df['GROSS_dem_IRR'][p2_s:p2_e],df['GROSS_dem_IRR'][p3_s:p3_e],
                df['GROSS_dem_IRR'][p4_s:p4_e]]
    ENV_DEM = [df['GROSS_dem_ENV'][0:p1],df['GROSS_dem_ENV'][p2_s:p2_e],df['GROSS_dem_ENV'][p3_s:p3_e],
                df['GROSS_dem_ENV'][p4_s:p4_e]]
    DEM_TOT = [df['GROSS_dem_tot'][0:p1],df['GROSS_dem_tot'][p2_s:p2_e],df['GROSS_dem_tot'][p3_s:p3_e],
                df['GROSS_dem_tot'][p4_s:p4_e]]

    DOM_UNM = [df['UNMET_DOM'][0:p1],df['UNMET_DOM'][p2_s:p2_e],df['UNMET_DOM'][p3_s:p3_e],
                df['UNMET_DOM'][p4_s:p4_e]]
    IND_UNM = [df['UNMET_IND'][0:p1],df['UNMET_IND'][p2_s:p2_e],df['UNMET_IND'][p3_s:p3_e],
                df['UNMET_IND'][p4_s:p4_e]]
    IRR_UNM = [df['UNMET_IRR'][0:p1],df['UNMET_IRR'][p2_s:p2_e],df['UNMET_IRR'][p3_s:p3_e],
                df['UNMET_IRR'][p4_s:p4_e]]
    ENV_UNM = [df['UNMET_ENV'][0:p1],df['UNMET_ENV'][p2_s:p2_e],df['UNMET_ENV'][p3_s:p3_e],
                df['UNMET_ENV'][p4_s:p4_e]]
    UNM_TOT = [df['UNMET_tot'][0:p1],df['UNMET_tot'][p2_s:p2_e],df['UNMET_tot'][p3_s:p3_e],
                df['UNMET_tot'][p4_s:p4_e]]
        
    fig, axes = plt.subplots(num=str(WP)+'_'+RCP+'_'+SSP+'_Gross_and_unmet_demand',nrows=2, ncols=1, 
                             figsize=plt.figaspect(0.75),sharex=True,sharey=True,dpi=110,
                             facecolor='white')
    
    
    bp = axes[0].boxplot(DOM_DEM,positions=[1,2,3,4],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    bp = axes[0].boxplot(IND_DEM,positions=[6,7,8,9],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    bp = axes[0].boxplot(IRR_DEM,positions=[11,12,13,14],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    bp = axes[0].boxplot(ENV_DEM,positions=[16,17,18,19],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    bp = axes[0].boxplot(DEM_TOT,positions=[21,22,23,24],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)    
    
    axes[0].set_title('Gross demand')   
    axes[0].yaxis.grid(True)
#    axes[0].set_ylim(ymax=600)
    
    
    bp = axes[1].boxplot(DOM_UNM,positions=[1,2,3,4],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    bp = axes[1].boxplot(IND_UNM,positions=[6,7,8,9],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    bp = axes[1].boxplot(IRR_UNM,positions=[11,12,13,14],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    bp = axes[1].boxplot(ENV_UNM,positions=[16,17,18,19],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)
    bp = axes[1].boxplot(UNM_TOT,positions=[21,22,23,24],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)    
    bp = axes[1].boxplot(UNM_TOT,positions=[21,22,23,24],widths = width,
                         showfliers=False,patch_artist=True)
    setBoxColors(bp)

    axes[1].set_title('Unmet demand')  
    
    for ax in axes.flatten():
        ax.set_xlim(0,25)
#        ax.set_ylim(ymin=-0.1)
        ax.set_yscale('log')
#        ax.yaxis.grid(True)
        ax.set_xticks([2.5, 7.5, 12.5, 17.5,22.5])
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom') 
        
    axes[1].set_xticklabels(['Domestic', 'Industry', 'Irrigation','Environment','Total'])
#    axes[1].set_ylim(ymax=axes[0].get_ylim()[1])
    
    fig.text(0.01, 0.5, r'Volume of water $\mathregular{(x10^6\ m^3month^{-1})}$', va='center', rotation='vertical')
    
    c = ['#8073ac','#e08214','#b35806','#7f3b08']
    
    h1, = axes[1].plot([1,1],c=c[0])
    h2, = axes[1].plot([1,1],c=c[1])
    h3, = axes[1].plot([1,1],c=c[2])
    h4, = axes[1].plot([1,1],c=c[3])
    axes[1].legend((h1,h2,h3,h4),('2006-2015','2020-2039','2050-2069','2080-2099'),
               ncol=4,loc=9,bbox_to_anchor=(0.5,-0.08),frameon=False,fontsize=12.5)
    h1.set_visible(False)
    h2.set_visible(False)
    h3.set_visible(False)
    h4.set_visible(False)    

    plt.suptitle('WP: '+str(WP)+' -- '+RCP+' '+SSP,fontsize=16)
    
    plt.tight_layout()
    plt.subplots_adjust(left=0.12,bottom=0.12,top=0.88)
    
    
    plt.show()    

    return fig
    
    
if __name__ =='__main__':
    box_DEM(WP,RCP,SSP,df,width)