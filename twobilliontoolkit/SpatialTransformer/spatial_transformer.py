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
    python path/to/spatial_transformer.py [-h] --input_path input_path --output_path output_path --gdb_path gdb_path --master master_data_path --load {datatracker,database} --save {datatracker,database} [--datatracker datatracker_path] [--attachments attachments_path] [--year YYYY] [--debug] [--suppress] [--resume]
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


from twobilliontoolkit.Logger.Logger import Logger
from twobilliontoolkit.SpatialTransformer.Parameters import Parameters
from twobilliontoolkit.SpatialTransformer.Processor import Processor
from twobilliontoolkit.RecordReviser.record_reviser import record_reviser
from twobilliontoolkit.NetworkTransfer.network_transfer import network_transfer
       
#========================================================
# Entry Function
#========================================================  
def spatial_transformer(input_path: str, output_path: str, load_from: str, save_to: str, gdb_path: str, datatracker: str, attachments: str, master_data_path: str, logger: Logger, database_config: str = None, year: str = None, debug: bool = False, resume: bool = False, skip_unzip: bool = False) -> None:
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
        logger (Logger): The Logger object to store and write to log files and the command line uniformly.
        database_config (str): Path to the database configuration file.
        year (str): Year of the entry being planted.
        debug (bool, optional): Determines if the program is in debug mode. Defaults False.
        resume (bool, optional): Determines if the program should resume from where a crash happened. Defaults False.
    """
    # Initialize a variable for the processor in case an error occurs beforehand
    spatial_processor = None
    
    try:       
        if database_config == "...":
            database_config = None
        elif database_config and not os.path.exists(database_config):
            raise("The database config file path you provided does not exist.")
            
        # Initialize Parameters class
        setup_parameters = Parameters(input_path, output_path, gdb_path, master_data_path, datatracker, attachments, logger, load_from, save_to, database_config, year,debug, resume)

        # Start the unzip tool 
        if skip_unzip:
            setup_parameters.output = setup_parameters.input
            logger.log(message=f'Skipping Ripple Unzipple, output is being set as the input. Now starting to create the datatracker entries from the files. Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
        else:
            setup_parameters.handle_unzip()
            logger.log(message=f'Ripple Unzipple has completed extracted the files. Now starting to create the datatracker entries from the files. Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
        

        # Create the GDB
        setup_parameters.create_gdb()
        
        # Initialize the SpatialData class
        spatial_processor = Processor(setup_parameters)
        
        # Search for any spatial data and create an entry in the datatracker for each one
        spatial_processor.create_datatracker_entries()
        logger.log(message=f'All entries have been created in the datatracker for the aspatial and spatial files. Now starting to process those found spatial files. Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
        
        # Go through the dictionary of entries and process them into the output geodatabase
        spatial_processor.process_entries()
        logger.log(message=f'The Processor has completed processing the files into the Geodatabase. Now starting to extract attachments from the Geodatabase. Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
        
        # Extract attachments from the Geodatabase
        spatial_processor.extract_attachments()
        logger.log(message=f'The Attachments Seeker has completed extracting the attachments from the geodatabase. Now starting to transfer over the files from the local directory to the specified output. Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')

        # Move the local files to the specified output except logs
        _ = network_transfer(
            local_path=spatial_processor.params.local_dir,
            network_path=os.path.dirname(spatial_processor.params.gdb_path),
            logger=logger,
            list_files=[os.path.basename(spatial_processor.params.gdb_path), os.path.basename(spatial_processor.params.datatracker), os.path.basename(spatial_processor.params.attachments)]
        )
        logger.log(message=f'The Network Transfer has completed moving the files from local to the network. Now saving the data. Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
                                      
        # Save the data tracker before returning
        spatial_processor.data.save_data(True if resume else False)
        logger.log(message=f'The changes have successfully been saved to the specified datatracker. Now opening Record Reviser. Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
        
        # Open the record reviser
        filter = {'created_at': datetime.datetime.now()}
        record_reviser(logger=logger, data=spatial_processor.data, gdb=spatial_processor.params.gdb_path, filter=filter)
        logger.log(message='The Record Reviser has completed editing any entries and is closing.', tag='INFO')

        # Commit all messages that have been posted to logger
        logger.commit(close=True)

        # Move the local logs to the specified output
        success = network_transfer(
            local_path=spatial_processor.params.local_dir,
            network_path=os.path.dirname(spatial_processor.params.gdb_path),
            logger=logger,
            list_files=[os.path.basename(logger.log_file)[:-4] + '_WARNING.txt', os.path.basename(logger.log_file)[:-4] + '_ERROR.txt']
        )

        if not debug and success:
            # Remove the local contents
            spatial_processor.del_gdb()
            os.mkdir(setup_parameters.local_dir)
            logger.log(message=f'Removing contents from the local directory completed. Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
            
    except (ValueError, Exception) as error:        
        # Log the error
        logger.log(message=traceback.format_exc(), tag='ERROR')
        
        # Save the data to the datatracker in case of crashing
        if spatial_processor:
            spatial_processor.data.save_data(True if resume else False)
            logger.log(message='A checkpoint has been made at the point of failure.', tag='INFO')
        
        # Commit all messages that have been posted to logger
        logger.commit()
        
        exit(1)
           
#========================================================
# Main
#========================================================
def main():
    """ The main function of the spatial_transformer.py script """
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='Spatial Transformer Tool')
    
    # Define command-line arguments
    parser.add_argument('--input_path', required=True, help='Directory or Compressed file location that will be handed to Ripple Unzipple.')
    parser.add_argument('--output_path', required=True, help='Where the final output of Ripple Unzipple will extract to.')
    parser.add_argument('--load', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to load from (datatracker or database).')
    parser.add_argument('--save', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to save to (datatracker or database).')
    parser.add_argument('--gdb_path', required=True, default='', help='Path of where the geodatabase will be saved, if it does not already exist, it will be created.')
    parser.add_argument('--datatracker', default='', help='Name of the datatracker file that will be saved adjacent to the geodatabase if provided.')
    parser.add_argument('--attachments', default='', help='Name of the attachments folder that will be saved adjacent to the geodatabase.')
    parser.add_argument('--master', default='', help='The location of the master aspatial datasheet.')
    parser.add_argument('--ini', default='', help='Path to the database initilization file. If not provided, then it will use the one provided in the repository.')
    parser.add_argument('--year', default='', help='The year that the planting occured for the entry.')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode.')
    parser.add_argument('--resume', action='store_true', default=False, help='Resume from where a crash happened.')
    parser.add_argument('--skip_unzip', action='store_true', default=False, help='Skip the recursive unzipping process if your input is already processed or unzipped. This will also overwrite your output location with the input.')
    parser.add_argument('--suppress', action='store_true', default=False, help='Suppress Warnings in the command-line and only show Errors.')
    parser.add_argument('--ps_script', default='', help='The location of the script to run commands if used.')
    
    # Parse the command-line arguments
    args = parser.parse_args()
        
    # Create the logfile path
    log_file = os.path.basename(args.gdb_path).replace('.gdb', f"_Log_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt")
        
    # Initialize the Logger
    logger = Logger(log_file=log_file, is_absolute_path=False, seperate_logs=True, suppress_warnings=args.suppress, script_path=args.ps_script, auto_commit=True, tool_name=os.path.abspath(__file__))
        
    # Get the start time of the script
    start_time = time.time()
    logger.log(message=f'Tool is starting... Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
        
    # Call the entry function
    spatial_transformer(input_path=args.input_path, output_path=args.output_path, load_from=args.load, save_to=args.save, gdb_path=args.gdb_path, datatracker=args.datatracker, attachments=args.attachments, master_data_path=args.master, logger=logger, database_config=args.ini, year=args.year, debug=args.debug, resume=args.resume, skip_unzip=args.skip_unzip)
    
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    logger.log(message=f'Tool has completed. Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
    logger.log(message=f'Elapsed time: {end_time - start_time:.2f} seconds', tag='INFO')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    