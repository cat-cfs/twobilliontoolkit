#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# twobilliontoolkit/BufferBuilder/buffer_builder.py
#========================================================
# Created By:       Anthony Rodway (Adapted from scripts written by Andrea Nesdoly)
# Email:            anthony.rodway@nrcan-rncan.gc.ca (andrea.nesdoly@nrcan-rncan.gc.ca)
# Creation Date:    Mon June 10 15:00:00 PST 2024
# Organization:     Natural Resources of Canada
# Team:             Carbon Accounting Team
#========================================================
# File Header
#========================================================
"""
File: twobilliontoolkit/BufferBuilder/buffer_builder.py
Created By:       Anthony Rodway (Adapted from scripts written by Andrea Nesdoly)
Email:            anthony.rodway@nrcan-rncan.gc.ca (andrea.nesdoly@nrcan-rncan.gc.ca)
Creation Date:    Mon June 10 15:00:00 PST 2024
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    The buffer_builder.py script is a Python tool for processing . 

Usage:
    python path/to/buffer_builder.py [-h] 
"""
#========================================================
# Imports
#========================================================
import os
import sys
import time
import shutil
import argparse
import datetime
import psycopg2
import configparser
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import wkt
import matplotlib.pyplot as plt
from shapely.geometry.multipolygon import MultiPolygon

from twobilliontoolkit.Logger.logger import log, Colors

from warnings import filterwarnings
filterwarnings("ignore", category=UserWarning, message='.*pandas only supports SQLAlchemy connectable.*')

#========================================================
# Globals
#========================================================
aliases = {
    "site": "BT_Legacy_ID__c",
    "size": "BT_Site_size__c",
    "province": "BT_Province__c",
    "lat": "BT_Geolocation__Latitude__s",
    "lon": "BT_Geolocation__Longitude__s",
    # Add more here if needed
}

# The soft-tolerance used to determine whether a point has changed enought to replace in the database. 
# Increase to be more leinent, Decrease to be more strict.
TOLERANCE = 1.3

#========================================================
# Entry Function
#========================================================  
def buffer_builder(data_sheet: str, database_ini: str, debug: bool = False) -> None:
    """
    The buffer_builder function 

    Args:
        data_sheet (str): Path to the datasheet to be proceesed into spatial geometries. Must be *.xlsx or *.csv.
        database_ini (str): Path to the .ini file with the database connection details
        debug (bool): A flag that when enabled will create intermediary shapefiles for checking the spatial data.
        
    Return:
        None
        
    """    
    try:       
        # Load the data into an initialized dataframe
        dataframe = pd.DataFrame()
        if data_sheet.endswith('.xlsx'):
            dataframe = pd.read_excel(data_sheet, usecols=aliases.values())
        elif data_sheet.endswith('.csv'):
            dataframe = pd.read_csv(data_sheet, usecols=aliases.values())
            
        # Invert the dictionary to use for renaming columns
        aliases_inverted = {v: k for k, v in aliases.items()}

        # Renaming the columns using the inverted aliases dictionary
        dataframe = dataframe.rename(columns=aliases_inverted)
        
        # Check for empty 'lat', 'lon', or 'site' values and drop corresponding entries
        dataframe.dropna(subset=['lat', 'lon', 'site'], inplace=True)

        # Set the 'site' column as integer type
        dataframe['site'] = dataframe['site'].astype('Int64')

        # Create a GeoDataFrame with geometry column from latitude and longitude
        geodataframe = gpd.GeoDataFrame(
            dataframe, 
            geometry=gpd.points_from_xy(dataframe.lon, dataframe.lat), 
            crs="EPSG:4326"
        )

        # Transform the CRS (Coordinate Reference System) to 'esri:102001'
        geodataframe_transformed = geodataframe.to_crs('esri:102001')

        # Convert size from hectares to square meters
        geodataframe_transformed['size_m2'] = geodataframe_transformed['size'] * 10000  # 1 hectare = 10,000 square meters

        # Calculate radius from the area
        geodataframe_transformed['radius'] = np.sqrt(geodataframe_transformed['size_m2'] / np.pi)

        # Create buffered geometries using the radius
        geodataframe_buffered = gpd.GeoDataFrame(
            geodataframe_transformed,
            geometry=geodataframe_transformed.buffer(geodataframe_transformed['radius']),
            crs=geodataframe_transformed.crs  # Keep the original CRS
        )

        # Define file paths for shapefiles
        points_shapefile = "C:/LocalTwoBillionToolkit/DebugShapefiles/Points.shp"
        buffered_shapefile = "C:/LocalTwoBillionToolkit/DebugShapefiles/Buffered.shp"
        
        if debug:
            # Ensure directory exists or create it
            if not os.path.exists(os.path.dirname(points_shapefile)):
                os.mkdir(os.path.dirname(points_shapefile))
            
            # Save GeoDataFrames to shapefiles
            geodataframe_transformed.to_file(points_shapefile, driver='ESRI Shapefile')
            geodataframe_buffered.to_file(buffered_shapefile, driver='ESRI Shapefile')
        else:
            # Remove directory if it exists
            if os.path.exists(os.path.dirname(points_shapefile)):
                shutil.rmtree(os.path.dirname(points_shapefile)) 

        # Read database configuration
        config_parse = configparser.ConfigParser()
        config_parse.read(database_ini)
        connectString = get_conn_str(config_parse)
        schema = config_parse['postgresql']['schema']

        # Query site points from database
        databasePoints = pd.read_sql_query(f'select site_id as site, ST_AsText(vp.geom) as database_geom_points from {schema}.valid_points vp', connectString)
        databasePoints['database_geom_points'] = gpd.GeoSeries.from_wkt(databasePoints['database_geom_points'], crs='esri:102001')

        # Query buffered site points from database
        databasePolygons = pd.read_sql_query(f'select site_id as site, ST_AsText(vbp.geom) as database_geom_buffered from {schema}.valid_buffered_points vbp', connectString)
        databasePolygons['database_geom_buffered'] = gpd.GeoSeries.from_wkt(databasePolygons['database_geom_buffered'], crs='esri:102001')

        # Merge database points and polygons with the transformed GeoDataFrame
        dataframe_master = pd.merge(databasePoints, databasePolygons, on='site', sort='site', how='outer')
        dataframe_master = pd.merge(dataframe_master, geodataframe_transformed, on='site', sort='site', how='outer')
        dataframe_master.rename(columns={'geometry': 'aspatial_geom_points'}, inplace=True)

        # Select buffered geometries and merge with the master DataFrame
        geodataframe_buffered_selected = geodataframe_buffered[['site', 'geometry']]
        dataframe_master = pd.merge(dataframe_master, geodataframe_buffered_selected, on='site', how='outer')
        dataframe_master.rename(columns={'geometry': 'aspatial_geom_buffered'}, inplace=True)

        # Sort DataFrame columns by index
        dataframe_master = dataframe_master.sort_index(axis=1)
        
        # Create GeoDataFrame for the master DataFrame
        geodataframe_master = gpd.GeoDataFrame(
            dataframe_master,
            geometry='aspatial_geom_points',
            crs='esri:102001'
        )
        
        # Extract x and y coordinates of aspatial and database points
        geodataframe_master['aspatial_geom_points_x'] = geodataframe_master['aspatial_geom_points'].x
        geodataframe_master['aspatial_geom_points_y'] = geodataframe_master['aspatial_geom_points'].y
        geodataframe_master['database_geom_points_x'] = geodataframe_master['database_geom_points'].x
        geodataframe_master['database_geom_points_y'] = geodataframe_master['database_geom_points'].y
        
        
        # Compare geometries with a tolerance
        geodataframe_master['almost_equals'] = geodataframe_master['aspatial_geom_points'].geom_equals_exact(geodataframe_master['database_geom_points'], tolerance=TOLERANCE)
        
        # Calculate distance between aspatial and database points
        geodataframe_master['point_distance'] = geodataframe_master['aspatial_geom_points'].distance(geodataframe_master['database_geom_points'])
        
        # Calculate areas of aspatial and database buffered geometries
        geodataframe_master['area_aspatial'] = geodataframe_master['aspatial_geom_buffered'].area
        geodataframe_master['area_database'] = geodataframe_master['database_geom_buffered'].area
        
        # Calculate the difference in area between aspatial and database geometries in hectares
        geodataframe_master['area_difference'] = abs(geodataframe_master['area_aspatial'] - geodataframe_master['area_database']) / 10000
            
        conn = get_conn(config_parse)
        cursor = conn.cursor()

        num_points_altered = 0
        num_buffered_points_altered = 0
        for index, row in geodataframe_master.iterrows():
            if np.isnan(row.site):
                continue
            
            # If the distance between the points is larger than the tolerance (in metres)
            if row.point_distance > TOLERANCE:                
                # If the point location different, update the existing point's dropped status to True
                cursor.execute(
                    "UPDATE bt_spatial_test.site_points SET dropped = True WHERE site_id = %s AND dropped = False",
                    (row.site,)
                )
            
                # Then insert the point into the database
                cursor.execute(
                    "INSERT INTO bt_spatial_test.site_points (site_id, geom, dropped) VALUES (%s, %s, %s)",
                    (row.site, "SRID=102001;" + row.aspatial_geom_points.wkt, False)
                )
                
                num_points_altered += 1
                
            # If the area difference between the buffered points is larger than the 1.0 HA (hectares)
            if row.area_difference > 1.0:
                # Update the previous buffered point entry to dropped
                cursor.execute(
                    "UPDATE bt_spatial_test.site_buffered_points SET dropped = True WHERE site_id = %s AND dropped = False",
                    (row.site,)
                )
            
                # Then insert the new buffered point into the database
                cursor.execute(
                    "INSERT INTO bt_spatial_test.site_buffered_points (site_id, geom, dropped) VALUES (%s, %s, %s)",
                    (row.site, "SRID=102001;" + MultiPolygon([wkt.loads(row.aspatial_geom_buffered.wkt)]).wkt, False)
                )
                
                num_buffered_points_altered += 1
          
        log(None, Colors.INFO, f"{num_points_altered} points have been altered.")
        log(None, Colors.INFO, f"{num_buffered_points_altered} buffered points have been altered.\n")      
                            
        # Commit the transaction
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

    except Exception as error:        
        # # Log the error
        # log(log_file, Colors.ERROR, traceback.format_exc())
        print(error)
        exit(1)
   
   
#========================================================
# Helper Functions
#========================================================
def get_conn(config):
    try:
        conn = psycopg2.connect(
            dbname=config['postgresql']['database'],
            user=config['postgresql']['user'],
            password=config['postgresql']['password'],
            host=config['postgresql']['host'],
            port=config['postgresql']['port']
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def get_conn_str(config):
    try:
        conn_str = "host='{}' port={} dbname='{}' user={} password='{}'".format(
            config['postgresql']['host'],
            config['postgresql']['port'],
            config['postgresql']['database'],
            config['postgresql']['user'],
            config['postgresql']['password']
        )
        conn = psycopg2.connect(conn_str)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None
        
#========================================================
# Main
#========================================================
def main():
    """ The main function of the buffer_builder.py script """
    # Get the start time of the script
    start_time = time.time()
    log(None, Colors.INFO, f'Tool is starting... Time: {datetime.datetime.now().strftime("%H:%M:%S")}')
    
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='Buffer Builder Tool')
    
    # Define command-line arguments
    parser.add_argument('--datasheet', required=True, help='Path to the asptial datasheet')
    parser.add_argument('--init', required=True, help='Path to the database initilization file')
    parser.add_argument('--debug', action='store_true', default=False, help='Flag for enabling debug mode')
    
    # Parse the command-line arguments
    args = parser.parse_args()
        
    # Call the entry function
    buffer_builder(args.datasheet, args.init, args.debug)
                        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, f'Tool has completed. Time: {datetime.datetime.now().strftime("%H:%M:%S")}')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    