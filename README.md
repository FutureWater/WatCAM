# WatCAM
Water and Climate Adaptation Model 
The Water and Climate Adaptation Model (WatCAM) allows the simulation of the water resources system at the basin or the so-called water province level. Water provinces are the intersection of the hydrological boundaries of river basins and the administrative boundaries of countries and provinces. For each water province, the model simulates the water balance and allocation to the principal sectoral demands. Allocation occurs depending on the priorities that can be modified between 1 (high priority) and 99 (low priority).

WatCAM relies on inputs from a hydrological model for streamflow and baseflow. For the development and testing, the outputs from the global hydrological model [PCR-GLOBWB](http://www.globalhydrology.nl/models/pcr-globwb-2-0/) have been used. But in principal, also other hydrological models can be used to provide water province-level flows under pristine conditions (i.e. not influenced by human interventions).

To run the model, call WatCAM_main.py in the root folder. Besides, the following folders are needed:
-	Input\ - input files
-	Output\ - output folder
-	Param\ - parameter files
-	SCRIPTS\ - additional scripts
-	GIS\ - shapefile with water provinces

For running the tool, only an installation of Python is required. For the development Python 2.7 was used, but probably the tool will run in more recent versions of Python also.

For more background information on the tool and details on the methods and equations behind the tool, and for referencing the WatCAM tool, please use:
-	Buitink, J., J.E. Hunink, P. Droogers, P. Torfs. 2016. Large scale adaptation strategies to climate change in the water-sector: An overview of the water allocation model WatCAM. [FutureWater Report 157](https://www.futurewater.nl/wp-content/uploads/2016/10/FW-report_WatCAM_JoostBuitink.pdf)

A scientific paper has been submitted recently and will likely be published during summer 2019.

The WatCAM tool was implemented in an interactive portal that allows running the tool and modifying a wide range of parameters. Please visit the [Water2Invest Web Service](http://w2i.geo.uu.nl/) to find out more.

For more information on the WatCAM tool, please contact Johannes Hunink (j.hunink@futurewater.es) 

The Water and Climate Adaptation Model (WatCAM) was developed by FutureWater. FutureWater is a research and consulting organization that works throughout the world combining scientific research with practical solutions for water resources planning and management.  For more information on FutureWater please visit our [website](http://futurewater.eu/).
