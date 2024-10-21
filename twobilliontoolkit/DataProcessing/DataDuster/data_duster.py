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
    The data_duster.py script is a Python tool for cleaning the geometry tables in the database by updating the 'site_geometry' 
    tables duplicate_geometries field.
    It connects to the database using configuration details, retrieves data, and updates duplicate geometries
    by triggering a database function.

Usage:
    python path/to/data_duster.py --ini path/to/db_config.ini --log path/to/log.txt [--ps_script path/to/ps_script.ps1] [--debug]

Arguments:
    --ini         : Path to the database configuration file.
    --log         : Path to the output log file.
    --ps_script   : Optional path to a PowerShell script used for additional commands.
    --debug       : Optional flag to enable debug mode.

Example:
    python ./data_duster.py --ini ../../SpatialTransformer/database.ini --log ./test_log.txt
"""
#========================================================
# Imports
#========================================================
import os
import sys
import time
import argparse
import datetime
import traceback

from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.SpatialTransformer.Database import Database

#========================================================
# Entry Function
#========================================================  
def data_duster(db_config: str, log_path: str = None, ps_script: str = None) -> None:
    """
    Entry function for cleaning data in the database.
    
    Args:
        db_config (str): Path to the database configuration file.
        log_path (str, Optional): Path to the log file to output any errors.
        ps_script (str, Optional): Path to the powershell script that was used to call the script if applicable.
    """      
    try:  
        # Create a database connection instance
        database_connection = Database()
        
        # Retrieve database connection parameters from the configuration file
        database_parameters = database_connection.get_params(db_config)
        
        # Call the function to update duplicate geometries in the database
        update_database_duplicate_geometries(database_connection, database_parameters, log_path, ps_script)

    except Exception as error:        
        # Log any exceptions that occur
        log(file_path=log_path, type=Colors.ERROR, message=traceback.format_exc(), ps_script=ps_script, absolute_provided=True)
      
#========================================================
# Helper Functions
#========================================================
def update_database_duplicate_geometries(database_connection: Database, database_parameters: dict[str, str], log_path: str = None, ps_script: str = None) -> None:
    """
    Updates each row in the site_geometry table to trigger the update_duplicate_geometry_ids_trigger.
    
    Args:
        database_connection (Database): Instance of the Database class.
        database_parameters (dict[str, str]): Dictionary of database connection parameters.
        log_path (str, Optional): Path to the log file to output any errors.
        ps_script (str, Optional): Path to the powershell script that was used to call the script if applicable.
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
    
    log_path = None
    if args.log:
        log_path = args.log,
    
    ps_script = None
    if args.ps_script:
        ps_script = args.ps_script
        
    # Call the entry function
    data_duster(args.ini, log_path, ps_script)
                        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, f'Tool has completed. Time: {datetime.datetime.now().strftime("%H:%M:%S")}')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    