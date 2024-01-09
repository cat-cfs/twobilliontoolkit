# spatial_transformer/common.py
#========================================================
# Imports
#========================================================
import os
import arcpy
import pandas as pd
import shutil
import sys
sys.path.append(r'\\vic-fas1\projects_a\2BT\02_Tools\2BT_Toolkit')

from RippleUnzipple.ripple_unzipple.ripple_unzipple import ripple_unzip, logging, Colors
from GeoAttachmentSeeker.geo_attachment_seeker.geo_attachment_seeker import find_attachments

#========================================================
# Globals
#========================================================
SPATIAL_FILE_EXTENSIONS = ('.shp', '.kml', '.kmz', '.geojson', '.gpkg', '.sqlite')
DATA_SHEET_EXTENSIONS = ('.xlsx', '.csv')
LAYOUT_FILE_EXTENSIONS = ('.mxd', '.aprx', '.pagx', '.qgs', '.qgz', '.qlr')
IMAGE_FILE_EXTENSIONS = ('pdf', '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif','.tiff')

DEBUG = False
