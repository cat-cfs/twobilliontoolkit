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
def data_duster() -> None:
    """
    The data_duster 

    Args:
        
    """    
    try:  
        pass

    except Exception as error:        
        # Log the error
        log(file_path=log_path, type=Colors.ERROR, message=traceback.format_exc(), ps_script=ps_script, absolute_provided=True)
        exit(1)
      
#========================================================
# Helper Functions
#========================================================

                       
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
    data_duster()
    
                        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, f'Tool has completed. Time: {datetime.datetime.now().strftime("%H:%M:%S")}')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    