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
    python spatial_transformer/spatial_transformer.py [-h] [--log_path LOG_PATH] [--debug] --load {datatracker,database} --save {datatracker,database} input_path output_path gdb_path data_tracker_path
"""
#========================================================
# Imports
#========================================================
from common import *
from ProcessorModule import Processor

import argparse
import sys
import time

#========================================================
# Classes
#========================================================
class StartupParameters:
    def __init__(self, input_path, output_path, gdb_path, data_tracker_path, master_data_path, log_path='', debug=False, load_from='database', save_to='database'):
       
        '''
        Initializes the StartupParameters class with input parameters.

        Parameters:
        - input_path (str): Path to input data.
        - output_path (str): Path to output data.
        - gdb_path (str): Path to geodatabase file.
        - data_tracker_path (str): Path to data tracker file.
        - master_data_path (str): Path to the aspatial master data.
        - log_path (str, optional): Path to log file. Defaults to an empty string.
        - debug (bool, optional): Determines if program is in debug mode
        ''' 
        # Ensure that if a datatracker is specified for loading or saving, then a path must be passed
        if (load_from == 'datatracker' or save_to == 'datatracker') and data_tracker_path == '':
            print('test')
            raise argparse.ArgumentTypeError("If --load or --save is 'datatracker', --data_tracker_path {path} must not be empty.")
        elif (load_from == 'datatracker' or save_to == 'datatracker') and data_tracker_path != '':
            self.validate_path(data_tracker_path, must_ends_with=DATA_SHEET_EXTENSIONS)
            
        # Validate and set paths
        self.validate_path(input_path, must_exists=True)
        self.validate_path(output_path)
        self.validate_path(gdb_path, must_ends_with='.gdb')
        self.validate_path(master_data_path, must_exists=True, must_ends_with='.xlsx')
        
        self.input = input_path
        self.output = output_path
        self.gdb = gdb_path
        self.datatracker = data_tracker_path
        self.masterdata = pd.read_excel(master_data_path)
        self.log = log_path
        self.debug = debug
        self.load_from = load_from
        self.save_to = save_to
        
        # Extra validation on master data to check it has project number column
        if 'Project Number' not in self.masterdata.columns:
            raise ValueError(f"The column 'Project Number' does not exist in the master data.")

        
    def validate_path(self, param, must_exists=False, must_ends_with=None):
        '''
        Validates the given path.

        Parameters:
        - param (str): Path to be validated.
        - must_exists (bool, optional): If True, the path must exist. Defaults to False.
        - must_ends_with (str, optional): If provided, the path must end with this string.

        Raises:
        - ValueError: If the path is not valid according to the specified conditions.
        
        Returns:
            None
        '''
        if not isinstance(param, str) or not param.strip():
            raise ValueError(f'{param} must be a non-empty string.')

        if must_ends_with is not None and not param.endswith(must_ends_with):
            raise ValueError(f'{param} must be of type {must_ends_with}.')

        if must_exists and not os.path.exists(param):
            raise ValueError(f'{param} path does not exist.')
    
    def handle_unzip(self):
        '''
        Handles the unzipping process using ripple_unzip.

        Calls the ripple_unzip function with input, output, and log paths.
        
        Returns:
            None
        '''
        ripple_unzip(self.input, self.output, self.log)
        
    def create_gdb(self):
        '''
        Creates a geodatabase file if it does not already exist.

        If the specified geodatabase file does not exist, it attempts to create one.
        
        Returns:
            None
        '''
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
                logging(self.log, Colors.INFO, f'Geodatabase: {file} created successfully')
            except arcpy.ExecuteError:
                logging(self.log, Colors.ERROR, arcpy.GetMessages(2))
        
    def __str__(self):
        '''
        Redefines the string representation of the class.

        Returns:
            str: String representation of the StartupParameters class.
        '''
        return f'\nStartupParameters Class\nInput path: {self.input}\nOutput path: {self.output}\nGeodatabase path: {self.gdb}\nDatatracker path: {self.datatracker}\nLog path: {self.log}\n' 
     
#========================================================
# Main
#========================================================
def main():
    """ The main function of the spatial_transformer.py script """
    # Get the start time of the script
    start_time = time.time()
    print(f'Tool is starting...')
    
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='This tools purpose is to ')
    
    # Define command-line arguments
    parser.add_argument('input_path', help='Input path')
    parser.add_argument('output_path', help='Output path')
    parser.add_argument('gdb_path', help='GDB path')
    parser.add_argument('--data_tracker_path', default='', help='Data tracker path')
    parser.add_argument('--log_path', default='', help='Log path (optional)')
    parser.add_argument('--master_data_path', default='', help='Master Aspatial Datasheet Path')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('--load', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to load from (datatracker or database)')
    parser.add_argument('--save', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to save to (datatracker or database)')
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the values using the attribute notation
    input_path = args.input_path
    output_path = args.output_path
    gdb_path = args.gdb_path
    data_tracker_path = args.data_tracker_path
    master_data_path = args.master_data_path
    log_path = args.log_path
    debug = args.debug
    load_from = args.load
    save_to = args.save
    
    try:        
        # Initialize StartupParameters class
        setup_parameters = StartupParameters(input_path, output_path, gdb_path, data_tracker_path, master_data_path, log_path, debug, load_from, save_to)
        
        # Uncomment to print out everything contained in class
        # print(setup_parameters)
        
        # # Start the unzip tool 
        setup_parameters.handle_unzip()
        
        # Create the GDB
        setup_parameters.create_gdb()

        # Initialize the SpatialData class
        spatial_data = Processor(setup_parameters)
        
        # Search for any spatial data and data sheets in the output directory
        spatial_data.search_for_spatial_data()
        
        # Uncomment to print out everything contained in class
        # print(spatial_data)
        
        # Start the processing
        spatial_data.process_spatial_files()
            
    except ValueError as error:
        logging(log_path, Colors.ERROR, error)
        exit(1)
    except Exception as error:
        logging(log_path, Colors.ERROR, error)
        exit(1)
                
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    print(f'\nTool has completed')
    print(f'Elapsed time: {end_time - start_time:.2f} seconds')


#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    