# Raster Best Fit Scatterplot

Raster Best Fit Scatterplot is a simple script for QGIS users which needs to use a simple analysis of the relation between two rasters. This script can draw a scatterplot of two rasters with the same spatial extent, size and number of pixels. Script uses four regression methods for analysis:

*linear regression
*logarithmic regression
*exponential regression
*power regression

Method selection is automatic and based on the best result of regression analysis (the highest regression coefficient). Rasters used for analysis should have the same spatial pattern (size and number of pixels).

Installation
------------

You need QGIS, version 2.x and an active Processing toolbox. Copy script files into the Scripts folder (see Processing/Options/Scripts/Scripts folder). Installing a script from the Processing tools panel: Scripts/Tools/Add script from file is also possible. The second way is easier; however, only a script without help is installed.
