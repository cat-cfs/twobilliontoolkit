# spatial_transformer/common.py
#========================================================
# Imports
#========================================================
import os
import datetime
import pandas as pd
import shutil
import sys

#========================================================
# Globals
#========================================================
SPATIAL_FILE_EXTENSIONS = ('.shp', '.kml', '.kmz', '.geojson', '.gpkg', '.sqlite')
DATA_SHEET_EXTENSIONS = ('.xlsx', '.csv', 'xls', 'docx')
LAYOUT_FILE_EXTENSIONS = ('.mxd', '.aprx', '.pagx', '.qgs', '.qgz', '.qlr')
IMAGE_FILE_EXTENSIONS = ('pdf', '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif','.tiff','.heic', '.mp4')
IGNORE_EXTENSIONS = ('.lock', '.cpg', '.dbf', '.prj', '.sbn', '.sbx', '.shx')
