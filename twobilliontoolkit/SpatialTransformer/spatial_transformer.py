#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# spatial_transformer/spatial_transformer.py
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
File:             spatial_transformer/spatial_transformer.py
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
import argparse
import arcpy
import sys
import time

import twobilliontoolkit.SpatialTransformer.common
from twobilliontoolkit.RippleUnzipple.ripple_unzipple import ripple_unzip
from twobilliontoolkit.SpatialTransformer.ProcessorModule import Processor


#========================================================
# Classes
#========================================================
class StartupParameters:
    def __init__(self, input_path, output_path, gdb_path, master_data_path, data_tracker_path, attachments_path, load_from='database', save_to='database', log_path=None, debug=False, resume=False):
       
        '''
        Initializes the StartupParameters class with input parameters.

        Parameters:
        - input_path (str): Path to input data.
        - output_path (str): Path to output data.
        - gdb_path (str): Path to geodatabase file.
        - master_data_path (str): Path to the aspatial master data.
        - load_from (str): Either 'database' or 'datatracker' to determine what to load the data from.
        - save_to (str): Either 'database' or 'datatracker' to determine what to save the data to.
        - data_tracker_path (str): Path to data tracker file.
        - attachments_path (str): Path where the extracted attachments will be.
        - log_path (str, optional): Path to log file. Defaults to an empty string.
        - debug (bool, optional): Determines if program is in debug mode
        - resume (bool, optional): Determines if program should resume from where a crash happened
        ''' 
        # Ensure that if a datatracker is specified for loading or saving, then a path must be passed
        if (load_from == 'datatracker' or save_to == 'datatracker') and data_tracker_path == '':
            raise argparse.ArgumentTypeError("If --load or --save is 'datatracker', --data_tracker_path must be specified.")
        elif (load_from == 'datatracker' or save_to == 'datatracker') and data_tracker_path != '':
            self.validate_path('data_tracker_path', data_tracker_path, must_ends_with=DATA_SHEET_EXTENSIONS)
            
        # If nothing was specified for the attachments path, set it to the same place as the output of the ripple unzipple tool.
        if attachments_path == '':
            attachments_path = output_path + 'Attachments'
            
        # Validate and set paths
        self.validate_path('input_path', input_path, must_exists=True)
        self.validate_path('output_path', output_path)
        self.validate_path('gdb_path', gdb_path, must_ends_with='.gdb')
        self.validate_path('master_data_path', master_data_path, must_exists=True, must_ends_with='.xlsx')
        self.validate_path('attachments_path', attachments_path)
        
        self.input = input_path
        self.output = output_path
        self.gdb = gdb_path
        self.masterdata = pd.read_excel(master_data_path)
        self.load_from = load_from
        self.save_to = save_to
        self.datatracker = data_tracker_path
        self.attachments = attachments_path
        self.log = log_path
        self.debug = debug
        self.resume = resume
        
        # Extra validation on master data to check it has project number column
        if 'Project Number' not in self.masterdata.columns:
            raise ValueError(f"The column 'Project Number' does not exist in the master data.")

        
    def validate_path(self, argument, param, must_exists=False, must_ends_with=None):
        '''
        Validates the given path.

        Parameters:
        - argument (str): The key value of the param passed.
        - param (str): Path to be validated.
        - must_exists (bool, optional): If True, the path must exist. Defaults to False.
        - must_ends_with (str, optional): If provided, the path must end with this string.

        Raises:
        - ValueError: If the path is not valid according to the specified conditions.
        
        Returns:
            None
        '''
        if not isinstance(param, str) or not param.strip():
            raise ValueError(f'{argument}: {param} must be a non-empty string.')

        if must_ends_with is not None and not param.endswith(must_ends_with):
            raise ValueError(f'{argument}: {param} must be of type {must_ends_with}.')

        if must_exists and not os.path.exists(param):
            raise ValueError(f'{argument}: {param} path does not exist.')
    
    def handle_unzip(self):
        '''
        Handles the unzipping process using ripple_unzip.

        Calls the ripple_unzip function with input, output, and log paths.
        
        Returns:
            None
        '''
        # If the resume after crash flag was specified, skip
        if self.resume:
            return
        
        ripple_unzip(self.input, self.output, self.log)
        
    def create_gdb(self):
        '''
        Creates a geodatabase file if it does not already exist.

        If the specified geodatabase file does not exist, it attempts to create one.
        
        Returns:
            None
        '''
        # If the resume after crash flag was specified, skip
        if self.resume:
            return
        
        # Create the .gdb if it does not already exists
        if not arcpy.Exists(self.gdb):
            try:
                # Create the directory if it does not exist
                directory_path = os.path.dirname(self.gdb)
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)

                # Create the file geodatabase
                file = os.path.basename(self.gdb)
                arcpy.management.CreateFileGDB(directory_path, file)
                
                log(None, Colors.INFO, f'Geodatabase: {file} created successfully')
            except arcpy.ExecuteError:
                log(self.log, Colors.ERROR, arcpy.GetMessages(2))
             
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
        
    try:        
        # Initialize StartupParameters class
        setup_parameters = StartupParameters(input_path, output_path, gdb_path, master_data_path, data_tracker_path, attachments_path, load_from, save_to, log_path, debug, resume)
        
        # Uncomment to print out everything contained in class
        # log(None, Colors.INFO, setup_parameters)
        
        # Start the unzip tool 
        setup_parameters.handle_unzip()
        
        # Create the GDB
        setup_parameters.create_gdb()

        # Initialize the SpatialData class
        spatial_data = Processor(setup_parameters)
        
        # Search for any spatial data and data sheets in the output directory
        spatial_data.search_for_spatial_data()
        
        # Uncomment to print out everything contained in class
        # log(None, Colors.INFO, spatial_data)
        
        # Start the processing
        spatial_data.process_spatial_files()
            
    except (ValueError, Exception) as error:
        # Log the error
        log(log_path, Colors.ERROR, error)
        
        # Save the data to the datatracker in case of crashing
        spatial_data.data._save_data()
        log(None, Colors.INFO, 'A checkpoint has been made at the point of faliure.')
        
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
    