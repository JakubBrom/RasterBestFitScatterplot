##Raster=group
##Input_raster_X=raster
##Input_raster_Y=raster
##Use_mask=boolean False
##Mask=raster

#-------------------------------------------------------------------------------
# Raster Best Fit Scatterplot 
#
# Author: Jakub Brom, University of South Bohemia in Ceske Budejovice,
#		  Faculty of Agriculture 
# Date: 2015-11-11
# Description: Raster Best Fit Scatterplot is a Python script providing simple 
# 			   regression analysis between two rasters and draw the scatterplot.
# 			   Script uses four regression method for analysis:
# 			   -linear
# 			   - logarithmic regression
# 			   - exponential regression
# 			   - power regression
# 			   Method selection is automatic and it is based on the best result
# 			   of regression analysis (the highest regression coefficient)
#
# License: Copyright (C) 2015, Jakub Brom
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------


import gdal
import sys, os
import numpy as np
import scipy.stats as scs
import pylab as pl
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException


def readGeo(rast, rast_mask=None):
	"""
	Function readGeo reads raster and mask files and makes 1d Numpy array with
	the data restricted by the mask.
	Inputs:
	- rast - raster in GDAL readable format
	- mask - raster mask in GDAL readable format. Data should be 8bit integer,
	         typicaly 0 (nodata) and 1 (data). 	
	"""
	
	# raster processing
	ds = gdal.Open(rast)
	try:
		array_in = gdal.Dataset.ReadAsArray(ds).astype(np.float32)
	except:
		raise GeoAlgorithmExecutionException('Error reading raster data. File might be too big.')
	ds = None
	rast_1d = np.ravel(array_in)                              # flattening of the data
	
	# mask processing
	if rast_mask != None:
		dsm = gdal.Open(rast_mask)
		try:
			array_mask = gdal.Dataset.ReadAsArray(dsm).astype(np.int8)
		except:
			raise GeoAlgorithmExecutionException('Error reading raster data. File might be too big.')
		dsm = None
		rast_1d_mask = np.ravel(array_mask)                    # flattening of the data
		mask_bool = np.ma.make_mask(rast_1d_mask)              # transformation of the mask in to the boolean
		rast_1d = rast_1d[mask_bool]		                   # exclusion of the "nodata" from the raster data
	else:
		pass

	return rast_1d

def regress_all(data_x, data_y):
	"""
	Regression analysis between two rasters. Analysis is calculated for all
	the linear,	ln, exp and power models. Outputs are lists with results of
	the models.
	Inputs:
		data_x - independent values
		data_y - dependent values
	Outputs:
		list_slope - list of slopes
		list_intercept - list of intercepts
		list_r - list of r values
		list_r2 - list of r-square values
		list_p - list of p values
		list_se - list of SE values
	"""

	ignore_zero = np.seterr(all = "ignore")
	
	list_x = [data_x, np.log(data_x), data_x, np.log(data_x)]
	list_y = [data_y, data_y, np.log(data_y), np.log(data_y)]
	
	# Calculation of constants for regression models: slope, intercept, r and p
	list_r = [int() for i in xrange(4)]                               	# list of r values for the methods
	list_r2 = [int() for i in xrange(4)]                                # list of r2 values for the methods
	list_slope = [int() for i in xrange(4)]								# list of slopes
	list_intercept = [int() for i in xrange(4)]							# list of intercepts
	list_p = [int() for i in xrange(4)]									# list of p values
	list_se = [int() for i in xrange(4)]								# list of SE values
	
	# Models - calculating regressions
	for i in xrange(len(list_x)):
		slope_lin, inter_lin, r_lin, p_lin, se_lin = scs.linregress(list_x[i],list_y[i])
		list_slope[i] = slope_lin
		list_r[i] = r_lin
		list_r2[i] = r_lin**2
		list_p[i] = p_lin
		list_se[i] = se_lin
		if i < 2:
			list_intercept[i] = inter_lin
		else:
			list_intercept[i] = np.exp(inter_lin)
			
	return list_slope, list_intercept, list_r, list_r2, list_p, list_se
	
def bestFit(list_p, list_r2):
	"""
	Setting regresion model according to max r-value for best-fit method.
	"""
	
	if min(list_p[:]) > 0.05:											
		print "There has not been calculated statistically significant result for any regression method used"
	
	model = list_r2.index(max(list_r2[:]))		# setting of regression model according to max r2 value
	
	return model


def comparPlot(x, y, intercept, slope, model, r2, name_x = None, name_y = None):
	"""
	Function draws scatterplot with regression line	for the given function.
	The regression equation and determination coefficient are written
	in the legend of the graph.
	
	Inputs:
		x - independent variable at X axis
		y - dependent variable at Y axis
		intercept - intercept of regr. model
		slope - slope of regr. model
		model - chosen regression model: 0 - linear, 1 - natural logarithm,
				2 - exponential, 3 power
		r2 - value of he determination coefficient 
	"""
	rmethod_name = ["Linear", "Nat. log.", "Exponential", "Power"]
	model_name = rmethod_name[model]
	
	t = np.linspace(min(x), max(x), 300) 		# x axis for regression line
	
	if model == 0:
		z_line = intercept + slope * t																# linear fit
		round_int = np.round(intercept, 3)
		round_sl = np.round(slope, 3)
		eq_name = r"$y={%s+x}{%s}$" % (round_int, round_sl)
	else:
		if model == 1:
			z_line = intercept + slope * np.log(t)													# nat. log. fit
			round_int = np.round(intercept, 3)
			round_sl = np.round(slope, 3)
			eq_name = r"$y={%s}+{%s}\ln{x}$" % (round_int, round_sl)
		else:
			if model == 2:
				z_line = intercept * np.exp(slope * t)												# exp. fit
				round_int = np.round(intercept, 3)
				round_sl = np.round(slope, 5)
				eq_name = r"$y={%s}\mathrm{e}^{{%s}{x}}$" % (round_int, round_sl)
			else:
				z_line = intercept * t ** slope														# pow. fit
				round_int = np.round(intercept, 3)
				round_sl = np.round(slope, 5)
				eq_name = r"$y={%s}{x}^{%s}$" % (round_int, round_sl)
	
	if r2 == 0.0:
		round_r2 = "-"
	else:
		round_r2 = np.round(r2, 3)
	
	str_r2 = r"$r^2=%s$" % str(round_r2)
	
	pl.title("Best fit regression")
	pl.plot(x,y,".")
	pl.plot(t,z_line, label = "Regression model (" + model_name + "): " + eq_name + "; " + str_r2, c = "black", linewidth = 2)
	
	pl.legend(loc='best')
	
	if name_x == None:
		name_x = "Axis X"
	else:
		path_to_folder, in_filename = os.path.split(name_x)
		name_x, ext = os.path.splitext(in_filename)
	if name_y == None:
		name_y = "Axis Y"
	else:
		path_to_folder, in_filename = os.path.split(name_y)
		name_y, ext = os.path.splitext(in_filename)
	
	pl.xlabel(str(name_x))
	pl.ylabel(str(name_y))
	

#-----------------------------------------------------------------------
# Processing of the Raster Best Fit Scatterplot  
rast_mask = Mask

if Use_mask == False:
    rast_mask = None
    

rast_1 = readGeo(Input_raster_X, rast_mask)
rast_2 = readGeo(Input_raster_Y, rast_mask)
    

if len(rast_1) != len(rast_2):
	raise GeoAlgorithmExecutionException("Size of the rasters differs.")
	
    
list_slope, list_intercept, list_r, list_r2, list_p, list_se = regress_all(rast_1, rast_2)
model = bestFit(list_p, list_r2)

slope = list_slope[model]
intercept = list_intercept[model]
r2 = list_r2[model]

comparPlot(rast_1, rast_2, intercept, slope, model, r2, Input_raster_X, Input_raster_Y)
pl.show()
