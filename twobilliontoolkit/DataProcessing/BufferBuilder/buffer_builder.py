#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# twobilliontoolkit/DataProcessing/BufferBuilder/buffer_builder.py
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
File: twobilliontoolkit/DataProcessing/BufferBuilder/buffer_builder.py
Created By:       Anthony Rodway (Adapted from scripts written by Andrea Nesdoly)
Email:            anthony.rodway@nrcan-rncan.gc.ca (andrea.nesdoly@nrcan-rncan.gc.ca)
Creation Date:    Mon June 10 15:00:00 PST 2024
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    The buffer_builder.py script is a Python tool for processing spatial data,
    creating buffer zones around given points, and integrating the results with 
    a PostgreSQL/PostGIS database. This script supports spatial analysis tasks 
    related to carbon accounting and land management.

Usage:
    python path/to/buffer_builder.py --datasheet <datasheet_path> --ini <database_ini_path> --log <log_file_path> [--debug] [--ps_script <script_path>]

Arguments:
    --datasheet     Path to the spatial data sheet (must be .csv or .xlsx).
    --ini           Path to the .ini file with database connection details.
    --log           Path to the output log file.
    --debug         Optional flag to enable debug mode, which saves intermediate shapefiles.
    --ps_script     Optional path to a PowerShell script for additional commands.

Example:
    python buffer_builder.py --datasheet data/spatial_data.csv --ini config/database.ini --log logs/buffer_builder.log --debug
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
import traceback
import configparser
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import wkt
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
DISTANCE_TOLERANCE = 1.3

# Another tolerance variable for the buffered points area checking
AREA_TOLERANCE = 1.0

# The location of the log file
log_path = None
# To indicate if the tool was run by a script
ps_script = None

#========================================================
# Entry Function
#========================================================  
def buffer_builder(data_sheet: str, database_ini: str, debug: bool = False) -> None:
    """
    The buffer_builder function processes a data sheet containing spatial geometries,
    buffers the points, and integrates them with database information.

    Args:
        data_sheet (str): Path to the datasheet to be processed into spatial geometries.
        Must be *.xlsx or *.csv.
        database_ini (str): Path to the .ini file with the database connection details.
        debug (bool): A flag that when enabled will create intermediary shapefiles
        for checking the spatial data.
    """    
    try:  
        # Perform some validation     
        if not os.path.exists(data_sheet):
            raise Exception(f"The Datasheet: {data_sheet} passed to Buffer Builder does not exist.")
        if not data_sheet.endswith('.xlsx') and not data_sheet.endswith('.csv'):
            raise Exception(f"The Datasheet: {data_sheet} passed to Buffer Builder must be an '.csv' or '.xlsx' file.")
        if not os.path.exists(database_ini):
            raise Exception(f"The database.ini file: {database_ini} passed to Buffer Builder does not exist.")
        
        # Load the data into an initialized dataframe
        dataframe = pd.DataFrame()
        if data_sheet.endswith('.xlsx'):
            dataframe = pd.read_excel(data_sheet, usecols=aliases.values())
        elif data_sheet.endswith('.csv'):
            dataframe = pd.read_csv(data_sheet, usecols=aliases.values())
            
        # Clean the dataframe
        dataframe = clean_dataframe(dataframe)

        # Create the Geodataframe with the points in ESRI:102001
        geodataframe_transformed = create_points(dataframe)

        # Buffer the point geometry in the geodataframe into polygons
        geodataframe_buffered = buffer_points(geodataframe_transformed)

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
        connection = get_connection(config_parse)
        schema = config_parse['postgresql']['schema']

        # Query site points from database
        databasePoints = query_database(connection, schema, 'valid_points', 'database_geom_points')
        
        # Query buffered site points from database
        databasePolygons = query_database(connection, schema, 'valid_buffered_points', 'database_geom_buffered')

        # Get lists of all site_ids that have a buffered point or point in the database
        point_site_ids = databasePoints.site.tolist()
        buffered_site_ids = databasePolygons.site.tolist()

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
        
        # Convert the master dataframe into a geodataframe and add additional useful fields
        geodataframe_master = build_master_geodataframe(dataframe_master)
                
        # Initialize the cursor 
        cursor = connection.cursor()
        
        # Add each entry of the master geodataframe to the database
        add_entries_to_database(cursor, geodataframe_master, schema, point_site_ids, buffered_site_ids)
                                    
        # Commit the transaction
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

    except Exception as error:        
        # Log the error
        log(file_path=log_path, type=Colors.ERROR, message=traceback.format_exc(), ps_script=ps_script, absolute_provided=True)
        exit(1)
      
#========================================================
# Helper Functions
#========================================================
def clean_dataframe(dataframe: pd.DataFrame):
    """
    Cleans the input dataframe by renaming columns, removing rows with missing 
    latitude, longitude, or site values, and setting the 'site' column to integer type.

    Args:
        dataframe (pd.DataFrame): The input dataframe to be cleaned.

    Returns:
        pd.DataFrame: The cleaned dataframe.
    """
    # Create a copy of the input dataframe
    result_dataframe = dataframe.copy()
    
    # Invert the dictionary to use for renaming columns
    aliases_inverted = {v: k for k, v in aliases.items()}

    # Renaming the columns using the inverted aliases dictionary
    result_dataframe = result_dataframe.rename(columns=aliases_inverted)
    
    # Check for empty 'lat', 'lon', or 'site' values and drop corresponding entries
    result_dataframe.dropna(subset=['lat', 'lon', 'site'], inplace=True)

    # Set the 'site' column as integer type
    result_dataframe['site'] = result_dataframe['site'].astype('Int64')
    
    return result_dataframe

def create_points(dataframe: pd.DataFrame):
    """
    Converts a dataframe with longitude and latitude columns into a GeoDataFrame 
    with point geometries and transforms the coordinate reference system to ESRI:102001.

    Args:
        dataframe (pd.DataFrame): A dataframe with at least two columns 'lon' and 
        'lat' to create the points.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame with point geometries in the ESRI:102001 
        (Canadian Albers) CRS.
    """
    # Create a GeoDataFrame with geometry column from latitude and longitude
    geodataframe = gpd.GeoDataFrame(
        dataframe, 
        geometry=gpd.points_from_xy(dataframe.lon, dataframe.lat), 
        crs="EPSG:4326"
    )

    # Transform the CRS (Coordinate Reference System) to 'esri:102001'
    geodataframe_transformed = geodataframe.to_crs('esri:102001')
    
    return geodataframe_transformed

def buffer_points(geodataframe: gpd.GeoDataFrame):
    """
    Creates buffered geometries around points in the input GeoDataFrame based on 
    a 'size' column representing area in hectares.

    Args:
        geodataframe (gpd.GeoDataFrame): A GeoDataFrame with point geometries and a 
        'size' column in hectares.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame with buffered geometries.
    """
    # Convert size from hectares to square meters
    geodataframe['size_m2'] = geodataframe['size'] * 10000  # 1 hectare = 10,000 square meters

    # Calculate radius from the area
    geodataframe['radius'] = np.sqrt(geodataframe['size_m2'] / np.pi)

    # Create buffered geometries using the radius
    geodataframe_buffered = gpd.GeoDataFrame(
        geodataframe,
        geometry=geodataframe.buffer(geodataframe['radius']),
        crs=geodataframe.crs  # Keep the original CRS
    )
    
    return geodataframe_buffered

def build_master_geodataframe(dataframe: pd.DataFrame):
    """
    Builds a master GeoDataFrame by creating geometries, extracting coordinates, 
    comparing geometries, and calculating distances and area differences.

    Args:
        dataframe (pd.DataFrame): A dataframe with columns for aspatial and database 
        geometries and their buffers.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame with added columns for coordinates, comparison 
        results, distances, and area differences.
    """
    # Create GeoDataFrame for the DataFrame
    geodataframe = gpd.GeoDataFrame(
        dataframe,
        geometry='aspatial_geom_points',
        crs='esri:102001'
    )
    
    # Extract x and y coordinates of aspatial and database points
    geodataframe['aspatial_geom_points_x'] = geodataframe['aspatial_geom_points'].x
    geodataframe['aspatial_geom_points_y'] = geodataframe['aspatial_geom_points'].y
    geodataframe['database_geom_points_x'] = geodataframe['database_geom_points'].x
    geodataframe['database_geom_points_y'] = geodataframe['database_geom_points'].y
    
    # Compare geometries with a tolerance
    geodataframe['almost_equals'] = geodataframe['aspatial_geom_points'].geom_equals_exact(geodataframe['database_geom_points'], tolerance=DISTANCE_TOLERANCE)
    
    # Calculate distance between aspatial and database points
    geodataframe['point_distance'] = geodataframe['aspatial_geom_points'].distance(geodataframe['database_geom_points'])
    
    # Calculate areas of aspatial and database buffered geometries
    geodataframe['area_aspatial'] = geodataframe['aspatial_geom_buffered'].area
    geodataframe['area_database'] = geodataframe['database_geom_buffered'].area
    
    # Calculate the difference in area between aspatial and database geometries in hectares
    geodataframe['area_difference'] = abs(geodataframe['area_aspatial'] - geodataframe['area_database']) / 10000
    
    return geodataframe

def add_entries_to_database(cursor: psycopg2.extensions.cursor, geodataframe: gpd.GeoDataFrame, schema: str, point_sites: list[int], buffered_sites: list[int]):
    """
    Adds or updates point and buffered point entries in the database based on 
    the provided GeoDataFrame, checking for differences and tolerances.

    Args:
        cursor (psycopg2.extensions.cursor): Database cursor for executing SQL commands.
        geodataframe (gpd.GeoDataFrame): A GeoDataFrame with site points and buffered 
        geometries.
        schema (str): The schema for the buffered and regular points to be inserted/updated.
        point_sites (list[int]): List of site IDs for points already in the database.
        buffered_sites (list[int]): List of site IDs for buffered points already in the 
        database.
    """
    # Loop through the rows of the master geodataframe and perform actions as needed
    num_points_added = 0
    num_points_altered = 0
    num_buffered_points_added = 0
    num_buffered_points_altered = 0
    for _, row in geodataframe.iterrows():
        if np.isnan(row.site):
            continue
    
        if row.aspatial_geom_points != None:
            # If the distance between the points is larger than the tolerance (in metres)
            if row.site in point_sites and not np.isnan(row.point_distance) and row.point_distance > DISTANCE_TOLERANCE:        
                # If the point location different, update the existing point's dropped status to True
                update_database_entry(cursor, schema + '.site_points', row.site)
            
                # Then insert the point into the database
                insert_database_entry(cursor, schema + '.site_points', row.site, row.aspatial_geom_points.wkt)
                
                num_points_altered += 1
            elif row.site not in point_sites:
                # Insert the point into the database
                insert_database_entry(cursor, schema + '.site_points', row.site, row.aspatial_geom_points.wkt)
                
                num_points_added += 1
           
        if row.aspatial_geom_buffered != None: 
            # If the area difference between the buffered points is larger than the tolerance (1.0 hectares)
            if row.site in buffered_sites and not np.isnan(row.area_difference) and row.area_difference > AREA_TOLERANCE:
                # Update the previous buffered point entry to dropped
                update_database_entry(cursor, schema + '.site_buffered_points', row.site)
            
                # Then insert the new buffered point into the database
                insert_database_entry(cursor, schema + '.site_buffered_points', row.site, MultiPolygon([wkt.loads(row.aspatial_geom_buffered.wkt)]).wkt)
                
                num_buffered_points_altered += 1
            elif row.site not in buffered_sites:
                # Insert the point into the database
                insert_database_entry(cursor, schema + '.site_buffered_points', row.site, MultiPolygon([wkt.loads(row.aspatial_geom_buffered.wkt)]).wkt)
                
                num_buffered_points_added += 1
          
    log(None, Colors.INFO, f"{num_points_added} new points have been added, {num_points_altered} points have been altered.")
    log(None, Colors.INFO, f"{num_buffered_points_added} new buffered points have been added, {num_buffered_points_altered} buffered points have been altered.\n")    

def get_connection(config: configparser.ConfigParser):
    """
    Takes a parsed config object from the configparser package, extracts the needed 
    variables to build and return a connection object.

    Args:
        config (configparser.ConfigParser): The parsed config to extract the variables
        from the database.ini file.

    Returns:
        psycopg2.extensions.connection: The connection parsed from the config to connect 
        to the database, or None if an error occurs.
    """
    try:
        connection = psycopg2.connect(
            dbname=config['postgresql']['database'],
            user=config['postgresql']['user'],
            password=config['postgresql']['password'],
            host=config['postgresql']['host'],
            port=config['postgresql']['port']
        )
        
        return connection
    except psycopg2.Error as error:
        # Log the error
        log(file_path=log_path, type=Colors.ERROR, message=f"Error connecting to PostgreSQL: {error}" + traceback.format_exc(), ps_script=ps_script, absolute_provided=True)
        return None
      
def query_database(connection: psycopg2.extensions.connection, schema: str, table: str, column_name: str):
    """
    Queries a PostgreSQL database to retrieve geometry data from a specified table 
    and column, returning the result as a GeoDataFrame.

    Args:
        connection (psycopg2.extensions.connection): The connection to the PostgreSQL database.
        schema (str): The schema where the table is located.
        table (str): The name of the table to query.
        column_name (str): The name of the geometry column to retrieve.

    Returns:
        pd.DataFrame: A DataFrame with 'site' and the specified geometry column.
    """
    # Query table from database to get geometry
    databasePoints = pd.read_sql_query(f'select site_id as site, ST_AsText(geom) as {column_name} from {schema}.{table}', connection)
    databasePoints[column_name] = gpd.GeoSeries.from_wkt(databasePoints[column_name], crs='esri:102001')
    
    return databasePoints
      
def update_database_entry(cursor: psycopg2.extensions.cursor, schema: str, site_id):
    """
    Updates a specific entry in the database to indicate it has been dropped (not to be used anymore).

    Args:
        cursor (psycopg2.extensions.cursor): The cursor connected to the database connection for executing SQL queries.
        schema (str): The schema the SQL query will be updating.
        site_id (int): The SiteID to indicate which entry to update in the database.
    """
    try:
        # Update the previous entry to dropped
        cursor.execute(
            f"UPDATE {schema} SET dropped = True WHERE site_id = %s AND dropped = False",
            (site_id,)
        )
    except Exception as error:
        # Log the error
        log(file_path=log_path, type=Colors.ERROR, message=f"Error connecting to PostgreSQL: {error}", ps_script=ps_script, absolute_provided=True)
    
def insert_database_entry(cursor: psycopg2.extensions.cursor, schema: str, site_id: int, geometry):
    """
    Inserts a buffered point entry into the database.

    Args:
        cursor (psycopg2.extensions.cursor): The cursor connected to the database connection for executing SQL queries.
        schema (str): The schema and table the SQL query will be inserting into.
        site_id (int): The SiteID to insert into the database.
        geometry: The Geometry to insert into the database.
    """
    try:
        # Insert the new geometry into the database
        cursor.execute(
            f"INSERT INTO {schema} (site_id, geom, dropped) VALUES (%s, %s, %s)",
            (site_id, f"SRID=102001;{geometry}", False)
        )
    except psycopg2.errors.ForeignKeyViolation as error:
        # Log the error
        log(file_path=log_path, type=Colors.ERROR, message=f"Error connecting to PostgreSQL: {error}" + traceback.format_exc(), ps_script=ps_script, absolute_provided=True)
                       
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
    parser.add_argument('--datasheet', required=True, help='Path to the asptial datasheet.')
    parser.add_argument('--ini', required=True, help='Path to the database initilization file.')
    parser.add_argument('--log', required=True, help='The location of the output log file for the tool.')
    parser.add_argument('--ps_script', default='', help='The location of the script to run commands if used.')
    parser.add_argument('--debug', action='store_true', default=False, help='Flag for enabling debug mode.')
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    global log_path
    global ps_script
    log_path = args.log
    if args.ps_script:
        ps_script = args.ps_script
        
    # Call the entry function
    buffer_builder(args.datasheet, args.ini, args.debug)
    
    
                        
         
                        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, f'Tool has completed. Time: {datetime.datetime.now().strftime("%H:%M:%S")}')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    