rm(list=ls())
require(rgdal)

ALLoutputType = c('FLO_internal','FLO_external','FLO_ava','RES_extracted',
                  'GWT_storage','GWT_inflow','GWT_extracted',
                 'GROSS_dem_DOM','GROSS_dem_IND','GROSS_dem_IRR','GROSS_dem_ENV',
                 'UNMET_DOM','UNMET_IND','UNMET_IRR','UNMET_ENV')
# ALLoutputType =c ('DESAL')

# Path to .csv data
path = 'c:/Users/Joost/Dropbox_offline/Global_results'

SCENs = c('RCP_2.6_SSP1','RCP_8.5_SSP5')
Adpts= c('Adpt_0','Adpt_1','Adpt_2','Adpt_3')

# Define location for and read SHP
GISpath = 'c:/Users/Joost/Dropbox_offline/Global_results/GIS'
ShapeWatProv = 'FINAL_final_map_world_2016'
shape <- readOGR(dsn = GISpath,ShapeWatProv)

for(SCEN in SCENs){
  for(Adpt in Adpts){
    layername = paste(SCEN,Adpt,sep='_')

    for(outputType in ALLoutputType){
      periods = c('Base','P3')
    
        # Read data
      data = read.table(paste(path,Adpt,SCEN,paste0('All_total_',outputType,'.csv'),sep='/'),header=TRUE,sep=',')
      
      # Create dataframe with the right row names (WatProvID)
      if(outputType == ALLoutputType[1]){
        df.gis = data.frame(data$WatProvID)
      }
      
      for(period in periods){
        colname = paste(outputType,period,sep='_')
        df.gis[colname] = data[period]
      }
      
      # colname = paste0(outputType,)
      # 
      # # Write the baseline data to the SH (other periods can be added as well)  
      # df.gis[outputType] = data$Base
      
    }
    
    cols = colnames(df.gis)
    
    cols = gsub("GROSS", "G", cols)
    cols = gsub("UNMET", "U", cols)
    cols = gsub("__", "_", cols)
    
    colnames(df.gis) <- cols
    
    df.gis[df.gis>1e+22] = NA
    df.gis[df.gis<0.01] = 0
    
    # Join the csv and shapefile
    joined <- merge(shape, df.gis, by.x="watprovID", by.y="data.WatProvID")
    # Change the layer CRS
    joined_CRS <- spTransform(joined,CRS("+proj=robin +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"))
    # Write the shapefile
    writeOGR(joined_CRS, dsn = GISpath, layer=layername, driver = "ESRI Shapefile",overwrite_layer=T)
  }
}


##################################################
########## CALCULATE VOLUMES PER PERIOD ##########
##################################################


# create temporary data fram, and drop row with no-data values
temp = joined_CRS@data
temp = temp[-c(314,315,329,337,591,898,899,900,1052,1053,1054,1129,1130,1131,1332),]
cols = c(colnames(df.gis))[-1]

df.global = data.frame(temp$watprovID)
for(col in cols){
  df.global[paste0(col,'_m3')] = temp[col] * 1e-3 * (temp$km2 * 1e6)
}
rownames(df.global) <- df.global$temp.watprovID
df.global$temp.watprovID <- NULL

df.summed = data.frame(c(0))
for (col in c(colnames(df.global))[-1]){
  df.summed[col] = sum(df.global[col])*1e-9
}

##################################################
########## CALCULATE VALUES PER COUNTRY ##########
##################################################

countries = unique(shape@data$COUNTRY)
df.country = data.frame(countries)
rownames(df.country) = countries

for (country in countries){
  cond = shape@data$COUNTRY==country
  for (col in colnames(df.global)){
    total = 0
    for (i in seq(length(cond))){
      if (cond[i] == TRUE){
        ID = as.character(i)
        if (is.null(df.global[ID,col])){
          val = 0
        } else if (is.na(df.global[ID,col])){
          val = 0
        } else{
          val = df.global[ID,col]
        }
        total = total + val
      }
    }
  df.country[country,col] = total * 1e-9
  }
}
# Remove columns
df.country$countries <- NULL
# df.country$c.0. <- NULL
# Order indexes A-Z
df.country <- df.country[order(rownames(df.country)),]