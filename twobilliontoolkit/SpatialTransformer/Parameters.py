# twobilliontoolkit/SpatialTransformer/Parameters.py
#========================================================
# Imports
#========================================================
import os
import arcpy
import argparse
import pandas as pd

from twobilliontoolkit.Logger.Logger import Logger
from twobilliontoolkit.SpatialTransformer.Database import Database
from twobilliontoolkit.RippleUnzipple.ripple_unzipple import ripple_unzip

#========================================================
# Classes
#========================================================
class Parameters:
    def __init__(self, input_path: str, output_path: str, gdb_path: str, master_data_path: str, datatracker: str, attachments: str, logger: Logger, load_from: str = 'database', save_to: str = 'database', debug: bool = False, resume: bool = False) -> None:
        """
        Initializes the Parameters class with input parameters.

        Args:
            input_path (str): Path to input data.
            output_path (str): Path to output data.
            gdb_path (str): Path to save the GeoDatabase.
            master_data_path (str): Path to the aspatial master data.
            logger (Logger): The Logger object to store and write to log files and the command line uniformly.
            load_from (str): Either 'database' or 'datatracker' to determine what to load the data from.
            save_to (str): Either 'database' or 'datatracker' to determine what to save the data to.
            datatracker (str): Datatracker file name.
            attachments (str): Attachment folder name.
            debug (bool, optional): Determines if the program is in debug mode.
            resume (bool, optional): Determines if the program should resume from where a crash happened.
        """
        self.local_dir = r'C:\LocalTwoBillionToolkit'
        
        # If nothing was specified for the attachments path, set it to the same place as the output of the ripple unzipple tool.
        if attachments == '':
            attachments = os.path.basename(gdb_path).replace('.gdb', '_Attachments')
            
        # Ensure that if a datatracker is specified for loading or saving, then a path must be passed
        if load_from == 'datatracker' or save_to == 'datatracker':
            if not datatracker:
                raise argparse.ArgumentTypeError("If --load or --save is 'datatracker', --datatracker must be specified.")
            else:
                self.validate_path('datatracker', datatracker, must_ends_with='.xlsx') 
                    
        if load_from == 'datatracker':
            if not master_data_path:
                raise argparse.ArgumentTypeError("If --load is 'datatracker', --master_data_path must be specified.")
            else:
                self.validate_path('master_data_path', master_data_path, must_exists=True, must_ends_with='.xlsx') 

        # Validate and set paths
        self.validate_path('input_path', input_path, must_exists=True)
        self.validate_path('output_network_path', output_path)
        self.validate_path('gdb_path', gdb_path, must_ends_with='.gdb')
              
        # Build the paths
        datatracker = os.path.join(self.local_dir, datatracker)
        attachments = os.path.join(self.local_dir, attachments)
                                
        self.input = input_path
        self.output = output_path
        self.gdb_path = gdb_path
        self.local_gdb_path = os.path.join(self.local_dir, os.path.basename(self.gdb_path))
        self.load_from = load_from
        self.save_to = save_to
        self.datatracker = datatracker
        self.attachments = attachments
        self.debug = debug
        self.resume = resume
        
        self.logger = logger
        
        self.project_numbers = self.get_project_numbers(master_data_path)

    def validate_path(self, argument: str, param: str, must_exists: bool = False, must_ends_with: bool = None) -> None:
        """
        Validates the given path.

        Args:
        - argument (str): The key value of the param passed.
        - param (str): Path to be validated.
        - must_exists (bool, optional): If True, the path must exist. Defaults to False.
        - must_ends_with (str, optional): If provided, the path must end with this string.

        Raises:
        - ValueError: If the path is not valid according to the specified conditions.
        """
        if not isinstance(param, str) or not param.strip():
            raise ValueError(f'{argument}: {param} must be a non-empty string.')

        if must_ends_with is not None and not param.endswith(must_ends_with):
            raise ValueError(f'{argument}: {param} must be of type {must_ends_with}.')

        if must_exists and not os.path.exists(param):
            raise ValueError(f'{argument}: {param} path does not exist.')
    
    def handle_unzip(self) -> None:
        """
        Handles the unzipping process using ripple_unzip.

        Calls the ripple_unzip function with input, output, and log paths.
        """
        # If the resume after crash flag was specified, skip
        if self.resume:
            return
        
        ripple_unzip(self.input, self.output, self.logger)
        
    def create_gdb(self) -> None:
        """
        Creates a geodatabase file if it does not already exist.

        If the specified geodatabase file does not exist, it attempts to create one.
        """
        # If the resume after crash flag was specified, skip
        if self.resume:
            return
        
        # Create the .gdb if it does not already exists
        if not arcpy.Exists(self.local_gdb_path):
            try:
                # Create the directory if it does not exist
                directory_path = os.path.dirname(self.local_gdb_path)
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)

                # Create the file geodatabase
                file = os.path.basename(self.local_gdb_path)
                arcpy.management.CreateFileGDB(directory_path, file)
                
                self.logger.log(message=f'Geodatabase: {file} created successfully', tag='INFO')
            except arcpy.ExecuteError:
                self.logger.log(message=arcpy.GetMessages(2), tag='ERROR')
                
    def get_project_numbers(self, master_datasheet: str = None) -> list[str]:
        """
        Get a list of project numbers from either the database or the master datasheet

        Returns:
            list[str]: A list of project numbers
        """
        if self.load_from == 'datatracker':                      
            masterdata = pd.read_excel(master_datasheet)
            
            # Extra validation on master data to check it has project number column
            if 'BT_Legacy_Project_ID__c' not in masterdata.columns:
                raise ValueError(f"The column 'BT_Legacy_Project_ID__c' does not exist in the master data.")
            
            # Convert masterdata to a list of strings
            return masterdata['BT_Legacy_Project_ID__c'].unique().tolist()
        
        # Create database object
        database_connection = Database(self.logger)
        
        # Read connection parameters from the configuration file
        database_parameters = database_connection.get_params()
        database_connection.connect(database_parameters)
        self.project_numbers = database_connection.read(
            database_connection.schema,
            table='project_number'
        )
        database_connection.disconnect()
        
        return [str(num[0]) for num in self.project_numbers]
        
        