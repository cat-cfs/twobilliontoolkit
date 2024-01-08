# spatial_transformer/common.py
#========================================================
# Imports
#========================================================
from ripple_unzipple import ripple_unzip, logging, Colors

import os
import arcpy
import pandas as pd
import shutil

#========================================================
# Globals
#========================================================
SPATIAL_FILE_EXTENSIONS = ('.shp', '.kml', '.kmz', '.geojson', '.gpkg', '.sqlite')
DATA_SHEET_EXTENSIONS = ('.xlsx', '.csv')
LAYOUT_FILE_EXTENSIONS = ('.mxd', '.aprx', '.pagx', '.qgs', '.qgz', '.qlr')
IMAGE_FILE_EXTENSIONS = ('pdf', '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif','.tiff')

DEBUG = False
