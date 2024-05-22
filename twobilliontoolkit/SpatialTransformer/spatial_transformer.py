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
    python path/to/spatial_transformer.py [-h] --input_path input_path [--output_path output_path] --gdb_path gdb_path --master master_data_path --load {datatracker,database} --save {datatracker,database} [--datatracker datatracker_path] [--attachments attachments_path] [--debug] [--suppress] [--resume]
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
from twobilliontoolkit.RecordReviser.record_reviser import call_record_reviser
from twobilliontoolkit.SpatialTransformer.network_transfer import transfer
       
#========================================================
# Entry Function
#========================================================  
def spatial_transformer(input_path: str, output_path: str, load_from: str, save_to: str, gdb_path: str, datatracker: str, attachments: str, master_data_path: str, debug: bool = False, resume: bool = False, suppress: bool = False, ps_script: str = None) -> None:
    """
    The spatial_transformer function serves as the main entry point for the spatial transformation script. Its primary purpose is to handle various tasks related to spatial data processing, such as starting the ripple_unzipple tool and geodatabase creation.

    Args:
        input_path (str): Path to the input directory or compressed file.
        output_path (str): Path to output data of Ripple Unzipple.
        load_from (str): Either 'database' or 'datatracker' to determine what to load the data from.
        save_to (str): Either 'database' or 'datatracker' to determine what to save the data to.
        gdb_path (str): Path to the Geodatabase.
        datatracker (str): Datatracker file name.
        attachments (str): Attachment folder name.
        master_data_path (str): Path to the aspatial master data.
        debug (bool, optional): Determines if the program is in debug mode. Defaults False.
        resume (bool, optional): Determines if the program should resume from where a crash happened. Defaults False.
        suppress (bool, optional): Determines if the program will suppress Warning Messages to the command line while running.
        ps_script (str, optional): The path location of the script to run spatial transformer.
    """
    # Create the logfile path
    log_file = os.path.basename(gdb_path).replace('.gdb', f"_Log_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt")
    
    # Initialize a variable for the processor in case an error occurs beforehand
    spatial_data = None
    
    try:       
        # Initialize Parameters class
        setup_parameters = Parameters(input_path, output_path, gdb_path, master_data_path, datatracker, attachments, load_from, save_to, log_file, debug, resume, suppress, ps_script)
        
        # Start the unzip tool 
        setup_parameters.handle_unzip()
        log(None, Colors.INFO, f'Ripple Unzipple has completed extracted the files. Now starting to create the datatracker entries from the files. Time: {datetime.now().strftime("%H:%M:%S")}')

        # Create the GDB
        setup_parameters.create_gdb()
        
        # Initialize the SpatialData class
        spatial_data = Processor(setup_parameters)
        
        # Search for any spatial data and create an entry in the datatracker for each one
        spatial_data.create_datatracker_entries()
        log(None, Colors.INFO, f'All entries have been created in the datatracker for the aspatial and spatial files. Now starting to process those found spatial files. Time: {datetime.now().strftime("%H:%M:%S")}')
        
        # Go through the dictionary of entries and process them into the output geodatabase
        spatial_data.process_entries()
        log(None, Colors.INFO, f'The Processor has completed processing the files into the Geodatabase. Now starting to extract attachments from the Geodatabase. Time: {datetime.now().strftime("%H:%M:%S")}')

        # # Search for any spatial data and data sheets in the output directory
        # spatial_data.search_for_spatial_data()
        # log(None, Colors.INFO, 'All spatial and aspatial files have been found when searching the output directory. Now starting to process those found spatial files.')
                
        # # Start the processing
        # spatial_data.process_spatial_files()
        # log(None, Colors.INFO, 'The Processor has completed processing the files into the Geodatabase. Now starting to extract attachments from the Geodatabase.')

        # Extract attachments from the Geodatabase
        spatial_data.extract_attachments()
        log(None, Colors.INFO, f'The Attachments Seeker has completed extracting the attachments from the geodatabase. Now starting to transfer over the files from the local directory to the specified output. Time: {datetime.now().strftime("%H:%M:%S")}')
        
        # Move the local files to the specified output
        transfer(
            spatial_data.params.local_dir,
            os.path.dirname(spatial_data.params.gdb_path),
            [os.path.basename(spatial_data.params.gdb_path), os.path.basename(spatial_data.params.datatracker), os.path.basename(spatial_data.params.attachments), spatial_data.params.log[:-4] + '_WARNING.txt', spatial_data.params.log[:-4] + '_ERROR.txt'],
            spatial_data.params.log
        )
        log(None, Colors.INFO, f'The Network Transfer has completed moving the files from local to the network. Now removing contents from the local directory. Time: {datetime.now().strftime("%H:%M:%S")}')
                   
        if not debug:
            # Remove the local contents
            shutil.rmtree(setup_parameters.local_dir)
            os.mkdir(setup_parameters.local_dir)
            log(None, Colors.INFO, f'Removing contents from the local directory completed. Now saving the changes to the specified data tracker. Time: {datetime.now().strftime("%H:%M:%S")}')
                   
        # Save the data tracker before returning
        spatial_data.data.save_data(True if resume else False)
        log(None, Colors.INFO, f'The changes have successfully been saved to the specified datatracker. Now opening Record Reviser. Time: {datetime.now().strftime("%H:%M:%S")}')
        
        # Open the record reviser
        call_record_reviser(spatial_data.data, spatial_data.params.gdb_path)
        log(None, Colors.INFO, 'The Record Reviser has completed editing any entries and is closing.')
            
    except (ValueError, Exception) as error:        
        # Log the error
        log(log_file, Colors.ERROR, traceback.format_exc(), ps_script=ps_script)
        
        # Save the data to the datatracker in case of crashing
        if spatial_data:
            spatial_data.data.save_data(True if resume else False)
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
    parser.add_argument('--input_path', required=True, help='Directory or Compressed file location that will be handed to Ripple Unzipple')
    parser.add_argument('--output_path', required=True, help='Where the final output of Ripple Unzipple will extract to.')
    parser.add_argument('--load', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to load from (datatracker or database)')
    parser.add_argument('--save', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to save to (datatracker or database)')
    parser.add_argument('--gdb_path', required=True, default='', help='Path of where the geodatabase will be saved, if it does not already exist, it will be created.')
    parser.add_argument('--datatracker', default='', help='Name of the datatracker file that will be saved adjacent to the geodatabase if provided')
    parser.add_argument('--attachments', default='', help='Name of the attachments folder that will be saved adjacent to the geodatabase')
    parser.add_argument('--master', default='', help='The location of the master aspatial datasheet')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('--resume', action='store_true', default=False, help='Resume from where a crash happened')
    parser.add_argument('--suppress', action='store_true', default=False, help='Suppress Warnings in the command-line and only show Errors')
    parser.add_argument('--ps_script', default='', help='The location of the script to run commands if used.')
    
    # Parse the command-line arguments
    args = parser.parse_args()
        
    # Call the entry function
    spatial_transformer(args.input_path, args.output_path, args.load, args.save, args.gdb_path, args.datatracker, args.attachments, args.master, args.debug, args.resume, args.suppress, args.ps_script)
                        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, 'Tool has completed')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    