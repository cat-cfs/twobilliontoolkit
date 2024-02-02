# twobilliontoolkit/SpatialTransformer/Datatracker.py
#========================================================
# Imports
#========================================================
import json
import psycopg2

# from twobilliontoolkit.SpatialTransformer.common import *
from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.SpatialTransformer.Database import Database

#========================================================
# Helper Class
#========================================================
class Datatracker:
    def __init__(self, data_traker_path: str, load_from: str = 'database', save_to: str = 'database', log_path: str = None) -> None:
        """
        Initializes the Data class with input parameters. Used to store the data tracker information.

        Args:
            data_traker_path (str): Path to data tracker to load data if exists.
            load_from (str): Flag to determine if loading dataframe should be done from the {database, datatracker}. Default: 'database'.
            save_to (str): Flag to determine if saving the dataframe should be done to the {database, datatracker}. Default: 'database'.
            log_path (str, optional): The path to the log file if you wish to keep any errors that occur.
        """
        self.data_dict = {}
        self.data_tracker = data_traker_path
        self.load_from = load_from
        self.save_to = save_to
        self.log_path = log_path
        self.database_connection = Database()
        
        self.load_data()
    
    def add_data(self, project_spatial_id: str, project_number: str, dropped: bool, project_path: str, raw_data_path: str, absolute_file_path: str, in_raw_gdb: bool, contains_pdf: bool, contains_image: bool, extracted_attachments_path: str, editor_tracking_enabled: bool, processed: bool) -> None:
        """
        Adds project data to the data tracker.

        Args:
            project_spatial_id (str): Project spatial ID. Acts as key in dictionary.
            project_number (str): Project number.
            dropped (bool): Indicates whether the entry is dropped, non-valid etc.
            project_path (str): Project path.
            raw_data_path (str): Raw data path.
            absolute_file_path (str): The full absolute file path.
            in_raw_gdb (bool): Indicates whether data is in raw GDB.
            contains_pdf (bool): Indicates whether data contains PDF files.
            contains_image (bool): Indicates whether data contains image files.
            extracted_attachments_path (str): The path to the extracted attachments if applicable.
            editor_tracking_enabled (bool): Indicates whether the editor tracking has been enabled for the layer in the gdb.
            processed (bool): Indicates whether data has been processed yet.
        """
        self.data_dict[project_spatial_id] = {
            'project_number': project_number,
            'project_path': project_path,
            'dropped': dropped,
            'raw_data_path': raw_data_path,
            'absolute_file_path': absolute_file_path,
            'in_raw_gdb': in_raw_gdb,
            'contains_pdf': contains_pdf,
            'contains_image': contains_image,
            'extracted_attachments_path': extracted_attachments_path,
            'editor_tracking_enabled': editor_tracking_enabled,
            'processed': processed
        }
        
    def set_data(self, project_spatial_id: str, project_number: str = None, dropped: bool = None, raw_data_path: str = None, absolute_file_path: str = None, in_raw_gdb: bool = None, contains_pdf: bool = None, contains_image: bool = None, extracted_attachments_path: str = None, editor_tracking_enabled: bool = None, processed: bool = None) -> None:
        """
        Updates project data in the data tracker.

        Args:
            project_spatial_id (str): Project spatial ID. Acts as key in dictionary.
            project_number (str): Project number (optional).
            dropped (bool): Indicates whether the entry is dropped, non-valid etc.
            raw_data_path (str): Raw data path (optional).
            absolute_file_path (str): The full absolute file path.
            in_raw_gdb (bool): Indicates whether data is in raw GDB (optional).
            contains_pdf (bool): Indicates whether data contains PDF files (optional).
            contains_image (bool): Indicates whether data contains image files (optional).
            extracted_attachments_path (str): The path to the extracted attachments if applicable (optional).
            editor_tracking_enabled (bool): Indicates whether the editor tracking has been enabled for the layer in the gdb (optional).
            processed (bool): Indicates whether data has been processed yet (optional).
        """
        # Update specified parameters as sets
        project_data = self.data_dict.get(project_spatial_id, {})
        if project_number is not None:
            project_data['project_number'] = project_number
        if dropped is not None:
            project_data['dropped'] = dropped
        if raw_data_path is not None:
            project_data['raw_data_path'] = raw_data_path
        if absolute_file_path is not None:
            project_data['absolute_file_path'] = absolute_file_path
        if in_raw_gdb is not None:
            project_data['in_raw_gdb'] = in_raw_gdb
        if contains_pdf is not None:
            project_data['contains_pdf'] = contains_pdf
        if contains_image is not None:
            project_data['contains_image'] = contains_image
        if extracted_attachments_path is not None:
            project_data['extracted_attachments_path'] = extracted_attachments_path
        if editor_tracking_enabled is not None:
            project_data['editor_tracking_enabled'] = editor_tracking_enabled
        if processed is not None:
            project_data['processed'] = processed
    
    def get_data(self, project_spatial_id: str) -> dict:
        """
        Gets an object of values given a project spatial id.

        Args:
            project_spatial_id (str): Project spatial ID. Acts as key in dictionary.

        Returns:
            dict: the values that correspond to the given key
        """
        return self.data_dict[project_spatial_id]
    
    def find_matching_spatial_id(self, raw_data_path: str) -> str:
        """
        Search for a matching entry for the raw data path.

        Args:
            raw_data_path (str): The path of the raw data.

        Returns:
            str: A matching project_spatial_id if it the raw data path already exists in the dataframe, otherwise return None.
        """        
        return next(
            (
                project_spatial_id
                for project_spatial_id, project_data in self.data_dict.items()
                if project_data.get('raw_data_path') == raw_data_path
            ),
            None
        )
        
    def find(self, criteria: dict) -> dict:
        """
        Find any criteria from the global data class.

        Args:
            criteria (dict): A dictionary of criteria of what to search the data class for.

        Returns:
            data_entry: A matching row of the dictionary if the criteria is all returned true, otherwise return None.
        """         
        return next(
            (
                data_entry
                for data_entry in self.data_dict.values()
                if all(data_entry.get(field) == value for field, value in criteria.items())
            ),
            None
        )
    
    def count_occurances(self, field: str, value) -> int:
        """
        Count the occurrences of a specified field in the data object.

        Args:
            field (str): Name of the parameter to count occurrences.
            value: Value of the parameter to count occurrences.

        Returns:
            int: Number of occurrences of the specified parameter.
        """
        return sum(
            1 for project_data in self.data_dict.values() if project_data.get(field) == value
        )
    
    def create_project_spatial_id(self, project_number: str) -> str:
        """
        Create the next project spatial id for the file

        Args:
            project_number (str): The formatted project number.

        Returns:
            str: The project spatial id next in line.
        """
        # Get the number of entries with the specified project number, add one because this is for the next entry
        result_occurrences = self.count_occurances('project_number', project_number) + 1
        
        # Clean the project number and format to the correct project_spatial_id format
        clean_project_number = project_number.replace('- ', '').replace(' ', '_')

        return clean_project_number + '_' + str(result_occurrences).zfill(2)
    
    def load_data(self) -> None:
        """
        Load data from an existing data tracker or a database connection into class.
        """
        if self.load_from == 'database':
            # Read connection parameters from the configuration file
            params = self.database_connection.get_params()
            
            self.database_connection.connect(params)
            
            rows = self.database_connection.read(
                table='bt_spatial_test.raw_data_tracker',
                columns=['project_spatial_id', 'project_number', 'dropped', 'project_path', 'raw_data_path', 'absolute_file_path', 'in_raw_gdb', 'contains_pdf', 'contains_image', 'extracted_attachments_path', 'editor_tracking_enabled']                
            )
                    
            # Initialize an empty dictionary to store the extracted data
            for fields in rows:
                # Extract the project_spatial_id from the row
                project_spatial_id = fields[0]

                # Extract the rest of the row values into a dictionary
                values = {
                    'project_number': fields[1],
                    'dropped': fields[2],
                    'project_path': fields[3],
                    'raw_data_path': fields[4],
                    'absolute_file_path': fields[5],
                    'in_raw_gdb': fields[6],
                    'contains_pdf': fields[7],
                    'contains_image': fields[8],
                    'extracted_attachments_path': fields[9],
                    'editor_tracking_enabled': fields[10],
                    'processed': True
                }
                
                # Store the values dictionary in the data_dict with project_spatial_id as the key
                self.data_dict[project_spatial_id] = values
                  
            self.database_connection.disconnect()      
            
        else:    
            # Check to see if the data tracker exists before loading from it
            if not os.path.exists(self.data_tracker):
                return
            
            # Read the data tracker
            data_df = pd.read_excel(
                self.data_tracker,
                dtype= { # Force types
                    'project_spatial_id': object,
                    'project_number': object,
                    'dropped': bool,
                    'project_path': object,
                    'raw_data_path': object,
                    'absolute_file_path': object,
                    'in_raw_gdb': bool,
                    'contains_pdf': bool,
                    'contains_image': bool,
                    'extracted_attachments_path': object,
                    'editor_tracking_enabled': bool,
                    'processed': bool
                }
            )

            # Use apply with a lambda function to add data to the data_dict
            data_df.apply(lambda row: self.add_data(
                row['project_spatial_id'],
                row['project_number'],
                row['dropped'],
                row['project_path'],
                row['raw_data_path'],
                row['absolute_file_path'],
                row['in_raw_gdb'],
                row['contains_pdf'],
                row['contains_image'],
                row['extracted_attachments_path'],
                row['editor_tracking_enabled'],
                row['processed']
            ), axis=1)

    def save_data(self, update: bool = False) -> None:
        """
        Save data tracker information to data tracker or database connection.
        
        Args:
            update (bool): Flag to determine if there are some entries in the data object that will need updating.
        """
        if self.save_to == 'database':     
            # Read connection parameters from the configuration file
            params = self.database_connection.get_params()
            
            self.database_connection.connect(params)
            
            rows = self.database_connection.read(
                table='bt_spatial_test.raw_data_tracker',
                columns=['project_spatial_id']
            )
            existing_ids = set(row[0] for row in rows)
  
            for key, value in self.data_dict.items():
                if key in existing_ids and update:
                    self.database_connection.update(
                        table='bt_spatial_test.raw_data_tracker',
                        values_dict={
                            'dropped': value['dropped'],
                            'in_raw_gdb': value['in_raw_gdb'], 
                            'contains_pdf': value['contains_pdf'], 
                            'contains_image': value['contains_image'],
                            'editor_tracking_enabled': value['editor_tracking_enabled']   
                        },
                        condition=f"project_spatial_id='{key}'"
                    )
                    
                elif key not in existing_ids:
                    self.database_connection.create(
                        table='bt_spatial_test.raw_data_tracker',
                        columns=('project_spatial_id', 'project_number', 'dropped', 'project_path', 'raw_data_path', 'absolute_file_path', 'in_raw_gdb', 'contains_pdf', 'contains_image', 'extracted_attachments_path', 'editor_tracking_enabled'),
                        values=(
                            key, 
                            value['project_number'], 
                            value['dropped'], 
                            value['project_path'], 
                            value['raw_data_path'],
                            value['absolute_file_path'], 
                            value['in_raw_gdb'], 
                            value['contains_pdf'], 
                            value['contains_image'],
                            value['extracted_attachments_path'],
                            value['editor_tracking_enabled']
                        )
                    ) 
            
            self.database_connection.disconnect()         

        else: 
            # Create a DataFrame and save it to Excel if the data tracker file doesn't exist
            df = pd.DataFrame(list(self.data_dict.values()), columns=['project_number', 'project_path', 'dropped', 'raw_data_path', 'absolute_file_path', 'in_raw_gdb', 'contains_pdf', 'contains_image', 'extracted_attachments_path', 'editor_tracking_enabled', 'processed'])

            # Add 'project_spatial_id' to the DataFrame
            df['project_spatial_id'] = list(self.data_dict.keys())

            # Reorder columns to have 'project_spatial_id' as the first column
            df = df[['project_spatial_id', 'project_number', 'dropped', 'project_path', 'raw_data_path', 'absolute_file_path', 'in_raw_gdb', 'contains_pdf', 'contains_image', 'extracted_attachments_path', 'editor_tracking_enabled', 'processed']]

            # Sort the rows by the project_spatial_id column
            df = df.sort_values(by=['project_spatial_id'])
            
            # Check if the directory exists, if not, create it
            directory = os.path.dirname(self.data_tracker)
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Convert dataframe to excel
            df.to_excel(self.data_tracker, index=False)
            
            log(None, Colors.INFO, f'The data tracker "{self.data_tracker}" has been created/updated successfully.')
