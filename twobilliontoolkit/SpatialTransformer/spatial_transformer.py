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
    python path/to/spatial_transformer.py [-h] --input_path input_path [--output_network_path output_path] --gdb gdb_path --master master_data_path --load {datatracker,database} --save {datatracker,database} [--datatracker datatracker_path] [--attachments attachments_path] [--debug] [--suppress] [--resume]
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
def spatial_transformer(input_path: str, output_path: str, load_from: str, save_to: str, gdb: str, datatracker: str, attachments: str, master_data_path: str, debug: bool = False, resume: bool = False, suppress: bool = False) -> None:
    """
    The spatial_transformer function serves as the main entry point for the spatial transformation script. Its primary purpose is to handle various tasks related to spatial data processing, such as starting the ripple_unzipple tool and geodatabase creation.

    Args:
        input_path (str): Path to the input directory or compressed file.
        output_path (str): Path to output data on network.
        load_from (str): Either 'database' or 'datatracker' to determine what to load the data from.
        save_to (str): Either 'database' or 'datatracker' to determine what to save the data to.
        gdb (str): Geodatabase name.
        datatracker(str): Datatracker file name.
        attachments (str): Attachment folder name.
        master_data_path (str): Path to the aspatial master data.
        debug (bool, optional): Determines if the program is in debug mode. Defaults False.
        resume (bool, optional): Determines if the program should resume from where a crash happened. Defaults False.
        suppress (bool, optional): Determines if the program will suppress Warning Messages to the command line while running.
    """
    # Create the logfile path
    log_path = gdb.replace('.gdb', f"_Log_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt")
    
    # Initialize a variable for the processor in case an error occurs beforehand
    spatial_data = None
    
    try:       
        # Initialize Parameters class
        setup_parameters = Parameters(input_path, output_path, gdb, master_data_path, datatracker, attachments, load_from, save_to, log_path, debug, resume, suppress)
                
        # Start the unzip tool 
        setup_parameters.handle_unzip()
        log(None, Colors.INFO, 'The input has been successfully extracted to the local directory C:\LocalTwoBillionToolkit\Output.')

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
    parser.add_argument('--input_path', required=True, default='', help='Directory or Compressed file location that will be handed to Ripple Unzipple')
    parser.add_argument('--output_network_path', required=False, default='', help='Where the final output will be transferred. Otherwise it remains in the local drive C:/LocalTwoBillionToolkit/Output')
    parser.add_argument('--load', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to load from (datatracker or database)')
    parser.add_argument('--save', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to save to (datatracker or database)')
    parser.add_argument('--gdb', required=True, default='', help='Name of the geodatabase that will be saved in the output network folder')
    parser.add_argument('--datatracker', default='', help='Name of the datatracker file that will be saved in the output network folder')
    parser.add_argument('--attachments', default='', help='Name of the attachments folder that will be saved in the output network folder')
    parser.add_argument('--master', required=True, default='', help='The location of the master aspatial datasheet')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('--resume', action='store_true', default=False, help='Resume from where a crash happened')
    parser.add_argument('--suppress', action='store_true', default=False, help='Suppress Warnings in the command-line and only show Errors')
    
    # Parse the command-line arguments
    args = parser.parse_args()
        
    # Call the entry function
    spatial_transformer(args.input_path, args.output_network_path, args.load, args.save, args.gdb, args.datatracker, args.attachments, args.master, args.debug, args.resume, args.suppress)
                        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, 'Tool has completed')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    