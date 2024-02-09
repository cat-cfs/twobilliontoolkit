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
    python path/to/spatial_transformer.py [-h] --input input_path --output output_path --gdb gdb_path --master master_data_path --load {datatracker,database} --save {datatracker,database} [--data_tracker data_tracker_path] [--attachments attachments_path] [--debug] [--resume]
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
# Entry Function
#========================================================  
def spatial_transformer(input_path: str, output_path: str, gdb_path: str, master_data_path: str, load_from: str, save_to: str, data_tracker_path: str, attachments_path: str, debug: bool = False, resume: bool = False) -> None:
    """
    The spatial_transformer function serves as the main entry point for the spatial transformation script. Its primary purpose is to handle various tasks related to spatial data processing, such as starting the ripple_unzipple tool and geodatabase creation.

    Args:
        input_path (str): Path to input data.
        output_path (str): Path to output data.
        gdb_path (str): Path to geodatabase file.
        master_data_path (str): Path to the aspatial master data.
        load_from (str): Either 'database' or 'datatracker' to determine what to load the data from.
        save_to (str): Either 'database' or 'datatracker' to determine what to save the data to.
        data_tracker_path (str): Path to data tracker file.
        attachments_path (str): Path where the extracted attachments will be.
        debug (bool, optional): Determines if the program is in debug mode. Defaults False.
        resume (bool, optional): Determines if the program should resume from where a crash happened. Defaults False.
    """
    # Create the logfile path
    log_path = gdb_path.replace('.gdb', f"{datetime.datetime.now().strftime('%Y-%m-%d')}.txt")
    
    # Initialize a variable for the processor in case an error occurs beforehand
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
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('--resume', action='store_true', default=False, help='Resume from where a crash happened')
    
    # Parse the command-line arguments
    args = parser.parse_args()
        
    # Call the entry function
    spatial_transformer(args.input, args.output, args.gdb, args.master, args.load, args.save, args.data_tracker, args.attachments,args.debug, args.resume)
                        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, 'Tool has completed')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    