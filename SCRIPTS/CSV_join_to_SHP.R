rm(list=ls())
require(rgdal)

ALLoutputType = c('FLO_internal','FLO_external','FLO_ava','RES_extracted',
                  'GWT_storage','GWT_inflow','GWT_extracted',
                 'GROSS_dem_DOM','GROSS_dem_IND','GROSS_dem_IRR','GROSS_dem_ENV',
                 'UNMET_DOM','UNMET_IND','UNMET_IRR','UNMET_ENV')
# ALLoutputType =c ('DESAL')

# Path to .csv data
path = 'c:/Users/Joost/Dropbox/W2I_Demo/MODEL/WatCam2016/WatCAM_paper/Output/WORLD_new_DESAL'

# periods = c('Base')#,'P3')

# Define location for SHP
GISpath = 'c:/Users/Joost/Dropbox/W2I_Demo/DATA/GIS_2016'
ShapeWatProv = 'FINAL_final_map_world_2016'
layername = 'All_PAPER_desal'
CountryLayer = paste0(layername,'_COUNTRY')

for(outputType in ALLoutputType){
  periods = c('Base','P3')

    # Read data
  data = read.table(paste(path,paste0('All_total_',outputType,'.csv'),sep='/'),header=TRUE,sep=',')
  
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
shape <- readOGR(dsn = GISpath,ShapeWatProv)
joined <- merge(shape, df.gis, by.x="watprovID", by.y="data.WatProvID")
# Change the layer CRS
joined_CRS <- spTransform(joined,CRS("+proj=robin +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"))
# Write the shapefile
writeOGR(joined_CRS, dsn = GISpath, layer=layername, driver = "ESRI Shapefile",overwrite_layer=T)

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

df.summed = data.frame(c(0))
for (col in c(colnames(df.global))[-1]){
  df.summed[col] = sum(df.global[col])*1e-9
}

# ##################################################
# ########## CALCULATE VALUES PER COUNTRY ##########
# ##################################################
# 
# SHPperCountry = shape
# 
# countries = unique(SHPperCountry@data$COUNTRY)
# 
# # ALLoutputType = c('FLO_internal','FLO_external','GWT_storage','GWT_inflow','GWT_extracted',
# #                   'GROSS_dem_DOM','GROSS_dem_IND','GROSS_dem_IRR','GROSS_dem_ENV','GROSS_dem_DWN',
# #                   'UNMET_DOM','UNMET_IND','UNMET_IRR','UNMET_ENV','UNMET_DWN')
# 
# ALLoutputType = gsub("GROSS", "G", ALLoutputType)
# ALLoutputType = gsub("UNMET", "U", ALLoutputType)
# ALLoutputType = gsub("__", "_", ALLoutputType)
# 
# for (country in countries){
#   cond = SHPperCountry@data$COUNTRY==country
#   for (outputTypeORIG in ALLoutputType){
#     for (period in periods){
#       outputType = paste(outputTypeORIG,period,sep='_')
#       newName = paste('C',outputType,sep='_')
#       total = 0
#       km2 = 0
#       for (i in seq(length(cond))){
#         if (cond[i] == TRUE){
#           if (is.null(joined_CRS@data[i,outputType])){
#             value = 0
#           } else if (is.na(joined_CRS@data[i,outputType])){
#             value = 0
#           }  else {
#             value = joined_CRS@data[i,outputType]
#           }
#           total = total + value
#           km2 = km2 + joined_CRS@data[i,'km2']
#         }}
#       for (i in seq(length(cond))){
#         if (cond[i] == TRUE){
#           SHPperCountry@data[i,'C_km2'] = km2
#           SHPperCountry@data[i,newName] = total
# }}}}}
# SHPperCountry <- spTransform(SHPperCountry,CRS("+proj=robin +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"))
# writeOGR(SHPperCountry, dsn = GISpath, layer=CountryLayer, driver = "ESRI Shapefile",overwrite_layer=T)
