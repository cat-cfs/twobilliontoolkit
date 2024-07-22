#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# twobilliontoolkit/DataProcessing/DataDuster/data_duster.py
#========================================================
# Created By:       Anthony Rodway 
# Email:            anthony.rodway@nrcan-rncan.gc.ca
# Creation Date:    Wed July 10 14:00:00 PST 2024
# Organization:     Natural Resources of Canada
# Team:             Carbon Accounting Team
#========================================================
# File Header
#========================================================
"""
File: twobilliontoolkit/DataProcessing/DataDuster/data_duster.py
Created By:       Anthony Rodway 
Email:            anthony.rodway@nrcan-rncan.gc.ca
Creation Date:    Wed July 10 14:00:00 PST 2024
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    The data_duster.py script is a Python tool for 

Usage:
    python path/to/data_duster.py

Arguments:


Example:
    python data_duster.py 
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
import traceback
import configparser
import numpy as np
import pandas as pd
import geopandas as gpd

from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.SpatialTransformer.Database import Database

#========================================================
# Globals
#========================================================
# The location of the log file
log_path = None
# To indicate if the tool was run by a script
ps_script = None

#========================================================
# Entry Function
#========================================================  
def data_duster(db_config: str) -> None:
    """
    Entry function for cleaning data in the database.
    
    Args:
        db_config (str): Path to the database configuration file.
    """      
    try:  
        # Create a database connection instance
        database_connection = Database()
        
        # Retrieve database connection parameters from the configuration file
        database_parameters = database_connection.get_params(db_config)
        
        # Call the function to update duplicate geometries in the database
        update_database_duplicate_geometries(database_connection, database_parameters)

    except Exception as error:        
        # Log any exceptions that occur
        log(file_path=log_path, type=Colors.ERROR, message=traceback.format_exc(), ps_script=ps_script, absolute_provided=True)
      
#========================================================
# Helper Functions
#========================================================
def update_database_duplicate_geometries(database_connection: Database, database_parameters: dict[str, str]) -> None:
    """
    Updates each row in the site_geometry table to trigger the update_duplicate_geometry_ids_trigger.
    
    Args:
        database_connection (Database): Instance of the Database class.
        database_parameters (dict[str, str]): Dictionary of database connection parameters.
    """
    try:
        # Connect to the database using the provided parameters
        database_connection.connect(database_parameters)
        
        # Read rows from the site_geometry table where the 'dropped' field is false
        rows = database_connection.read(database_connection.schema, 'site_geometry', condition="dropped = false")
        
        # Iterate over each row to update the 'id' field (to trigger the update trigger)
        for row in rows:
            update_query = f"UPDATE {database_connection.schema}.site_geometry SET id = {row[0]} WHERE id = {row[0]}"
            database_connection.execute(update_query)
    
    except Exception as error:        
        # Log any exceptions that occur
        log(file_path=log_path, type=Colors.ERROR, message=traceback.format_exc(), ps_script=ps_script, absolute_provided=True)
        
    finally:
        # Ensure the database connection is closed
        database_connection.disconnect()
                       
#========================================================
# Main
#========================================================
def main():
    """ The main function of the data_duster.py script """
    # Get the start time of the script
    start_time = time.time()
    log(None, Colors.INFO, f'Tool is starting... Time: {datetime.datetime.now().strftime("%H:%M:%S")}')
    
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='Data Duster Tool')
    
    # Define command-line arguments
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
    data_duster(args.ini)
                        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, f'Tool has completed. Time: {datetime.datetime.now().strftime("%H:%M:%S")}')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    