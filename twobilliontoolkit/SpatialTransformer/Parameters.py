# twobilliontoolkit/SpatialTransformer/Parameters.py
#========================================================
# Imports
#========================================================
import arcpy
import argparse

from twobilliontoolkit.SpatialTransformer.common import *
from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.RippleUnzipple.ripple_unzipple import ripple_unzip

#========================================================
# Classes
#========================================================
class Parameters:
    def __init__(self, input_path: str, output_path: str, gdb_path: str, master_data_path: str, datatracker_path: str, attachments_path: str, load_from: str = 'database', save_to: str = 'database', log_path: str = None, debug: bool = False, resume: bool = False, suppress: bool = False) -> None:
        """
        Initializes the Parameters class with input parameters.

        Args:
        - input_path (str): Path to input data.
        - output_path (str): Path to output data.
        - gdb_path (str): Path to geodatabase file.
        - master_data_path (str): Path to the aspatial master data.
        - load_from (str): Either 'database' or 'datatracker' to determine what to load the data from.
        - save_to (str): Either 'database' or 'datatracker' to determine what to save the data to.
        - datatracker_path (str): Path to data tracker file.
        - attachments_path (str): Path where the extracted attachments will be.
        - log_path (str, optional): Path to log file. Defaults to an empty string.
        - debug (bool, optional): Determines if the program is in debug mode.
        - resume (bool, optional): Determines if the program should resume from where a crash happened.
        - suppress (bool, optional): Determines if the program will suppress warnings to the command line.
        """
        # Ensure that if a datatracker is specified for loading or saving, then a path must be passed
        if (load_from == 'datatracker' or save_to == 'datatracker') and datatracker_path == '':
            raise argparse.ArgumentTypeError("If --load or --save is 'datatracker', --datatracker_path must be specified.")
        elif (load_from == 'datatracker' or save_to == 'datatracker') and datatracker_path != '':
            self.validate_path('datatracker_path', datatracker_path, must_ends_with=DATA_SHEET_EXTENSIONS)
            if resume:
                self.validate_path('datatracker_path', datatracker_path, must_exists=True)
            
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
        self.datatracker = datatracker_path
        self.attachments = attachments_path
        self.log = log_path
        self.debug = debug
        self.resume = resume
        self.suppress = suppress
        
        # Extra validation on master data to check it has project number column
        if 'Project Number' not in self.masterdata.columns:
            raise ValueError(f"The column 'Project Number' does not exist in the master data.")

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
        
        ripple_unzip(self.input, self.output, self.log)
        
    def create_gdb(self) -> None:
        """
        Creates a geodatabase file if it does not already exist.

        If the specified geodatabase file does not exist, it attempts to create one.
        """
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