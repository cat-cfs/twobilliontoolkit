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
    A tool for cleaning the geometry tables in the database by updating the 'site_geometry' table's duplicate_geometries field. 
    It connects to the database using configuration details, retrieves data, and updates duplicate geometries by triggering a database function.

Usage:
    python path/to/data_duster.py --ini <database_ini_path> --log <log_file_path> [--ps_script <script_path>] [--debug]

Arguments:
    --ini           Path to the database configuration file (INI format).
    --log           Path to the log file.
    --ps_script     Optional path to a PowerShell script for additional operations.
    --debug         Optional flag to enable debug mode.

Example:
    python data_duster.py --ini database.ini --log data_duster.txt --debug
"""
#========================================================
# Imports
#========================================================
import sys
import time
import argparse
import datetime
import traceback

from twobilliontoolkit.Logger.Logger import Logger
from twobilliontoolkit.SpatialTransformer.Database import Database

#========================================================
# Entry Function
#========================================================  
def data_duster(db_config: str, logger: Logger) -> None:
    """
    Entry function for cleaning data in the database.
    
    Args:
        db_config (str): Path to the database configuration file.
        logger (Logger): The Logger object to store and write to log files and the command line uniformly.
    """      
    try:  
        # Create a database connection instance
        database_connection = Database(logger)
        
        # Retrieve database connection parameters from the configuration file
        database_parameters = database_connection.get_params(db_config)
        
        # Call the function to update duplicate geometries in the database
        update_database_duplicate_geometries(database_connection, database_parameters, logger)

    except Exception as error:        
        # Log any exceptions that occur
        logger.log(message=traceback.format_exc(), tag='ERROR')
      
#========================================================
# Helper Functions
#========================================================
def update_database_duplicate_geometries(database_connection: Database, database_parameters: dict[str, str], logger: Logger) -> None:
    """
    Updates each row in the site_geometry table to trigger the update_duplicate_geometry_ids_trigger.
    
    Args:
        database_connection (Database): Instance of the Database class.
        database_parameters (dict[str, str]): Dictionary of database connection parameters.
        logger (Logger): The Logger object to store and write to log files and the command line uniformly.
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
        logger.log(message=traceback.format_exc(), tag='ERROR')
        
    finally:
        # Ensure the database connection is closed
        database_connection.disconnect()
                       
#========================================================
# Main
#========================================================
def main():
    """ The main function of the data_duster.py script """    
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='Data Duster Tool - A tool to clean duplicate geometries in the site_geometry table of the database.')
    
    # Define command-line arguments
    parser.add_argument('--ini', required=True, help='Path to the database configuration file (INI format).')
    parser.add_argument('--log', required=True, help='Path to the log file.')
    parser.add_argument('--ps_script', default='', help='Optional path to a PowerShell script for additional operations.')
    parser.add_argument('--debug', action='store_true', default=False, help='Optional flag to enable debug mode.')
        
    # Parse the command-line arguments
    args = parser.parse_args()
        
    # Initialize the Logger
    logger = Logger(log_file=args.log, script_path=args.ps_script, auto_commit=True, tool_name=os.path.abspath(__file__))
        
    # Get the start time of the script
    start_time = time.time()
    logger.log(message=f'Tool is starting... Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
        
    # Call the entry function
    data_duster(args.ini, logger)
                        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    logger.log(message=f'Tool has completed. Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
    logger.log(message=f'Elapsed time: {end_time - start_time:.2f} seconds', tag='INFO')
    
    # Commit all messages that have been posted to logger
    logger.commit(close=True)

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    