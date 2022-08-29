from netCDF4 import Dataset, num2date, date2num
import pdb
import numpy as np
import shutil
import glob
import os
from datetime import datetime, timedelta
import time
from numpy.random import uniform

'''
This program will add the attributes that Irina said should be there:

:RangeBeginningDate = "2022-02-04" ;
:RangeBeginningTime = "01:18:04.443205" ;
:RangeEndingDate = "2022-02-04" ;
:RangeEndingTime = "22:51:49.014062" ;
:ProductionDateTime = "2022-06-27 18:35:13.743443" ;
:IdentifierProductDOI = "10.5067/582L7HTJ343N" ; (DOI, not URL)

the spatial attributes that I need:
:WestBoundingCoordinate =
:NorthBoundingCoordinate =
:EastBoundingCoordinate = 
:SouthBoundingCoordinate =

'''



rootpath = '/home/thearty/acdisc/ftp/data/misc/FLEXPART/'

shortname = 'BCFLEXPART'

filepath = rootpath+shortname+'.1'
    
filenames = glob.glob(filepath+'/*.nc')


for filename in filenames:

    print(filename)

    dataset = Dataset(filename, 'r+')

    # fix the DOI
    dataset.IdentifierProductDOI = str(dataset.IdentifierProductDOI.split(dataset.IdentifierProductDOIAuthority)[-1])

    # add the spatial attributes that I need:
    dataset.WestBoundingCoordinate = -180.
    dataset.NorthBoundingCoordinate = 90.
    dataset.EastBoundingCoordinate = 180.
    dataset.SouthBoundingCoordinate = -90.

    # add the production time
    day,month,year = dataset.created_date_UTC.split('-')
    dataset.ProductionDateTime = '-'.join([year,month,day])+' '+dataset.created_hour_UTC

    # add the range beggining and ending date and time
    time = dataset.variables['time'][:]
    time_coverage_start = num2date(time[0], dataset.variables['time'].units)
    time_coverage_end = num2date(time[-1], dataset.variables['time'].units) + timedelta(days=1) - timedelta(seconds=1) # this will make the end time the end of the day

    # these are the DPDG recommendations
    dataset.time_coverage_start = time_coverage_start.strftime("%Y-%m-%d %H:%M:%S")
    dataset.time_coverage_end = time_coverage_end.strftime("%Y-%m-%d %H:%M:%S")

    # these are the GES DISC recommendations
    dataset.RangeBeginningDate = time_coverage_start.strftime("%Y-%m-%d")
    dataset.RangeBeginningTime = time_coverage_start.strftime("%H:%M:%S")
    dataset.RangeEndingDate = time_coverage_end.strftime("%Y-%m-%d")
    dataset.RangeEndingTime =time_coverage_end.strftime("%H:%M:%S")

    # Here are some example edits to varible metadata
    
    dataset['/geophysical_data/Longitude'].units = 'degrees_east'
    dataset['/geophysical_data/Longitude'].long_name = 'longitude'
    dataset['/geophysical_data/Longitude'].standard_name = 'longitude'

    dataset['/geophysical_data/Latitude'].units = 'degrees_north'
    dataset['/geophysical_data/Latitude'].long_name = 'latitude'
    dataset['/geophysical_data/Latitude'].standard_name = 'latitude'

    # Coordinate variables should not have fill values
    if '_FillValue' in dataset['/geophysical_data/Longitude'].ncattrs():
        dataset['/geophysical_data/Longitude'].delncattr('_FillValue')

    if '_FillValue' in dataset['/geophysical_data/Latitude'].ncattrs():
        dataset['/geophysical_data/Latitude'].delncattr('_FillValue')


    
    dataset.close()

