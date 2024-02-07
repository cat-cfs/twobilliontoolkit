#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# twobilliontoolkit/SpatialTransformer/spatial_transformer.py
#========================================================
# Created By:       Anthony Rodway
# Email:            anthony.rodway@nrcan-rncan.gc.ca
# Creation Date:    Wed November 15 10:30:00 PST 2023
# Organization:     Natural Resources of Canada
# Team:             Carbon Accounting Team
#========================================================
# File Header
#========================================================
"""
File: twobilliontoolkit/SpatialTransformer/spatial_transformer.py
Created By:       Anthony Rodway
Email:            anthony.rodway@nrcan-rncan.gc.ca
Creation Date:    Wed November 15 10:30:00 PST 2023
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    The spatial_transformer.py script is a Python tool for processing spatial data. It handles tasks like geodatabase creation, file validation, and checking project numbers against a master data sheet. 

Usage:
    python path/to/spatial_transformer.py [-h] --input input_path --output output_path --gdb gdb_path --master master_data_path --load {datatracker,database} --save {datatracker,database} [--data_tracker data_tracker_path] [--attachments attachments_path] [--log LOG_PATH] [--debug] [--resume]
"""
#========================================================
# Imports
#========================================================
import sys
import time
import argparse
import traceback

from twobilliontoolkit.SpatialTransformer.common import *
from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.SpatialTransformer.Parameters import Parameters
from twobilliontoolkit.SpatialTransformer.Processor import Processor
       
#========================================================
# Main
#========================================================
def main():
    """ The main function of the spatial_transformer.py script """
    # Get the start time of the script
    start_time = time.time()
    log(None, Colors.INFO, 'Tool is starting...')
    
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='Spatial Transformer Tool')
    
    # Define command-line arguments
    parser.add_argument('--input', required=True, default='', help='Directory or Compressed file location that will be handed to Ripple Unzipple')
    parser.add_argument('--output', required=True, default='', help='Where to output the result from Ripple Unzipple')
    parser.add_argument('--gdb', required=True, default='', help='The new location or where an exsiting Geodatabase is located')
    parser.add_argument('--master', required=True, default='', help='The location of the master aspatial datasheet')
    parser.add_argument('--load', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to load from (datatracker or database)')
    parser.add_argument('--save', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to save to (datatracker or database)')
    parser.add_argument('--data_tracker', default='', help='The new location or where an exsiting data tracker is located')
    parser.add_argument('--attachments', default='', help='The location where the attachments will be extracted to if applicable (optional, defaults to same root output as Ripple Unzipple)')
    parser.add_argument('--log', default=None, help='The new location or where an existing log file is located (optional)')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('--resume', action='store_true', default=False, help='Resume from where a crash happened')
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the values using the attribute notation
    input_path = args.input
    output_path = args.output
    gdb_path = args.gdb
    master_data_path = args.master
    load_from = args.load
    save_to = args.save
    data_tracker_path = args.data_tracker
    attachments_path = args.attachments
    log_path = args.log
    debug = args.debug
    resume = args.resume
        
    spatial_data = None
    try:        
        # Initialize Parameters class
        setup_parameters = Parameters(input_path, output_path, gdb_path, master_data_path, data_tracker_path, attachments_path, load_from, save_to, log_path, debug, resume)
                
        # Start the unzip tool 
        setup_parameters.handle_unzip()
        
        # Create the GDB
        setup_parameters.create_gdb()
        
        # Initialize the SpatialData class
        spatial_data = Processor(setup_parameters)
        
        # Search for any spatial data and data sheets in the output directory
        spatial_data.search_for_spatial_data()
                
        # Start the processing
        spatial_data.process_spatial_files()
            
    except (ValueError, Exception) as error:
        # Print the traceback
        traceback.print_exc()

        # Get the traceback information
        exc_type, exc_value, exc_traceback = sys.exc_info()

        # Extract the filename and line number where the exception was raised
        trace = traceback.extract_tb(exc_traceback)[-1]
        filename = trace[0]
        line_number = trace[1]
        
        # Log the error
        log(log_path, Colors.ERROR, error, filename, line_number)
        
        # Save the data to the datatracker in case of crashing
        if spatial_data:
            spatial_data.data.save_data()
            log(None, Colors.INFO, 'A checkpoint has been made at the point of failure.')
        
        exit(1)
                        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, 'Tool has completed')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')


#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    