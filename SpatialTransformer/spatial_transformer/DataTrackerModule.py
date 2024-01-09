# spatial_transformer/DataTrackerModule.py
#========================================================
# Imports
#========================================================
from common import *

import json

#========================================================
# Helper Class
#========================================================
class DataTracker:
    def __init__(self, data_traker_path, load_from='database', save_to='database'):
        '''
        Initializes the Data class with input parameters. Used to store the data tracker information.

        Parameters:
            data_traker_path (str): Path to data tracker to load data if exists.
            load_from (str): Flag to determine if loading dataframe should be done from the {database, datatracker}. Default: 'database'.
            save_to (str): Flag to determine if saving the dataframe should be done to the {database, datatracker}. Default: 'database'.

        Returns:
            None
        '''
        self.data_dict = {}
        self.data_tracker = data_traker_path
        self.load_from = load_from
        self.save_to = save_to
        
        if os.path.exists(data_traker_path):
            self._load_data()
    
    def add_data(self, project_spatial_id, project_number, project_path, raw_data_path, in_raw_gdb, contains_pdf, contains_image, attachments_path):
        '''
        Adds project data to the data tracker.

        Parameters:
            project_spatial_id (int): Project spatial ID. Acts as key in dictionary.
            project_number (int): Project number.
            project_path (str): Project path.
            raw_data_path (str): Raw data path.
            in_raw_gdb (bool): Indicates whether data is in raw GDB.
            contains_pdf (bool): Indicates whether data contains PDF files.
            contains_image (bool): Indicates whether data contains image files.
            attachments_path (str): The path to the extracted attachments if applicable.

        Returns:
            None
        '''
        self.data_dict[project_spatial_id] = {
            'project_number': project_number,
            'project_path': project_path,
            'raw_data_path': raw_data_path,
            'in_raw_gdb': in_raw_gdb,
            'contains_pdf': contains_pdf,
            'contains_image': contains_image,
            'attachments_path': attachments_path
        }
        
    def set_data(self, project_spatial_id, project_number=None, raw_data_path=None, in_raw_gdb=None, contains_pdf=None, contains_image=None, attachments_path=None):
        '''
        Updates project data in the data tracker.

        Parameters:
            project_spatial_id (str): Project spatial ID. Acts as key in dictionary.
            project_number (str): Project number (optional).
            raw_data_path (str): Raw data path (optional).
            in_raw_gdb (bool): Indicates whether data is in raw GDB (optional).
            contains_pdf (bool): Indicates whether data contains PDF files (optional).
            contains_image (bool): Indicates whether data contains image files (optional).
            attachments_path(str): The path to the extracted attachments if applicable. (optional)

        Returns:
            None
        '''
        # Update specified parameters as sets
        project_data = self.data_dict.get(project_spatial_id, {})
        if project_number is not None:
            project_data['project_number'] = project_number
        if raw_data_path is not None:
            project_data['raw_data_path'] = raw_data_path
        if in_raw_gdb is not None:
            project_data['in_raw_gdb'] = in_raw_gdb
        if contains_pdf is not None:
            project_data['contains_pdf'] = contains_pdf
        if contains_image is not None:
            project_data['contains_image'] = contains_image
        if attachments_path is not None:
            project_data['attachments_path'] = attachments_path
    
    def get_data(self, project_spatial_id):
        '''
        Gets an object of values given a project spatial id.

        Parameters:
            project_spatial_id (int): Project spatial ID. Acts as key in dictionary.

        Returns:
            dict: the values that correspond to the given key
        '''
        return self.data_dict[project_spatial_id]
    
    def _find_matching_spatial_id(self, raw_data_path):
        '''
        Search for a matching entry for the raw data path.

        Parameters:
            raw_data_path (str): The path of the raw data.

        Returns:
            str: A matching project_spatial_id if it the raw data path already exists in the dataframe, otherwise return None.
        '''       
        #
        return next(
            (
                project_spatial_id
                for project_spatial_id, project_data in self.data_dict.items()
                if project_data.get('raw_data_path') == raw_data_path
            ),
            None
        )
    
    def _count_occurances(self, field, value):
        '''
        Count the occurrences of a specified field in the data object.

        Parameters:
            field (str): Name of the parameter to count occurrences.
            value: Value of the parameter to count occurrences.

        Returns:
            int: Number of occurrences of the specified parameter.
        '''
        return sum(
            1 for project_data in self.data_dict.values() if project_data.get(field) == value
        )
    
    def _create_project_spatial_id(self, project_number):
        '''
        Create the next project spatial id for the file

        Parameters:
            project_number (str): The formatted project number.

        Returns:
            str: The project spatial id next in line.
        '''
        # Get the number of entries with the specified project number, add one because this is for the next entry
        result_occurrences = self._count_occurances('project_number', project_number) + 1
        
        # Clean the project number and format to the correct project_spatial_id format
        clean_project_number = project_number.replace('- ', '').replace(' ', '_')

        return clean_project_number + '_' + str(result_occurrences)
    
    def _load_data(self):
        """
        Load data from an existing data tracker or a database connection into class.

        Returns:
            None
        """
        if self.load_from == 'database':
            # TODO: add functionality to connect and add data to dataframe from the database
            print('Loading from database is currently not implemented, please try again with the data tracker excel sheets.')
            exit(1)
            
        else:    
            # Read the data tracker
            data_df = pd.read_excel(self.data_tracker)

            # Use apply with a lambda function to add data to the data_dict
            data_df.apply(lambda row: self.add_data(
                row['project_spatial_id'],
                row['project_number'],
                row['project_path'],
                row['raw_data_path'],
                row['in_raw_gdb'],
                row['contains_pdf'],
                row['contains_image'],
                row['attachments_path']
            ), axis=1)

    def _save_data(self, save_to='database'):
        """
        Save data tracker information to data tracker or database connection.

        Returns:
            None
        """
        if self.save_to == 'database':
            # TODO: add functionality to connect and add data from dataframe to database
            print('Saving to database is currently not implemented, please try again with the data tracker excel sheets.')
            exit(1)
        
        else: 
            # Create a DataFrame and save it to Excel if the data tracker file doesn't exist
            df = pd.DataFrame(list(self.data_dict.values()), columns=['project_number', 'project_path', 'raw_data_path', 'in_raw_gdb', 'contains_pdf', 'contains_image', 'attachments_path'])

            # Add 'project_spatial_id' to the DataFrame
            df['project_spatial_id'] = list(self.data_dict.keys())

            # Reorder columns to have 'project_spatial_id' as the first column
            df = df[['project_spatial_id', 'project_number', 'project_path', 'raw_data_path', 'in_raw_gdb', 'contains_pdf', 'contains_image', 'attachments_path']]

            # Sort the rows by the project_spatial_id column
            df = df.sort_values(by=['project_spatial_id'])
            
            # Check if the directory exists, if not, create it
            directory = os.path.dirname(self.data_tracker)
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Convert dataframe to excel
            df.to_excel(self.data_tracker, index=False)
                
    def __str__(self):
        '''
        Redefines the string representation of the class.

        Returns:
        - str: String representation of the Data class.
        '''
        # Returning Pretty JSON
        return f'\nData Class\nData Dictionary: {json.dumps(self.data_dict, indent=4)}'
    