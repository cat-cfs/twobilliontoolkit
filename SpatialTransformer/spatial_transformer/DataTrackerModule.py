# spatial_transformer/DataTrackerModule.py
#========================================================
# Imports
#========================================================
from common import *

import json
import psycopg2

from config import config

SCHEMA='bt_spatial_test'

#========================================================
# Helper Class
#========================================================
class DataTracker:
    def __init__(self, data_traker_path, load_from='database', save_to='database', log_path=None):
        '''
        Initializes the Data class with input parameters. Used to store the data tracker information.

        Parameters:
            data_traker_path (str): Path to data tracker to load data if exists.
            load_from (str): Flag to determine if loading dataframe should be done from the {database, datatracker}. Default: 'database'.
            save_to (str): Flag to determine if saving the dataframe should be done to the {database, datatracker}. Default: 'database'.
            log_path (str, optional): The path to the log file if you wish to keep any errors that occur.

        Returns:
            None
        '''
        self.data_dict = {}
        self.data_tracker = data_traker_path
        self.load_from = load_from
        self.save_to = save_to
        self.log_path = log_path
        
        self._load_data()
    
    def add_data(self, project_spatial_id, project_number, project_path, raw_data_path, absolute_file_path, in_raw_gdb, contains_pdf, contains_image, extracted_attachments_path, processed):
        '''
        Adds project data to the data tracker.

        Parameters:
            project_spatial_id (int): Project spatial ID. Acts as key in dictionary.
            project_number (int): Project number.
            project_path (str): Project path.
            raw_data_path (str): Raw data path.
            absolute_file_path (str): The full absolute file path.
            in_raw_gdb (bool): Indicates whether data is in raw GDB.
            contains_pdf (bool): Indicates whether data contains PDF files.
            contains_image (bool): Indicates whether data contains image files.
            extracted_attachments_path (str): The path to the extracted attachments if applicable.
            processed (bool): Indicates whether data has been processed yet.

        Returns:
            None
        '''
        self.data_dict[project_spatial_id] = {
            'project_number': project_number,
            'project_path': project_path,
            'raw_data_path': raw_data_path,
            'absolute_file_path': absolute_file_path,
            'in_raw_gdb': in_raw_gdb,
            'contains_pdf': contains_pdf,
            'contains_image': contains_image,
            'extracted_attachments_path': extracted_attachments_path,
            'processed': processed
        }
        
    def set_data(self, project_spatial_id, project_number=None, raw_data_path=None, absolute_file_path=None, in_raw_gdb=None, contains_pdf=None, contains_image=None, extracted_attachments_path=None, processed=None):
        '''
        Updates project data in the data tracker.

        Parameters:
            project_spatial_id (str): Project spatial ID. Acts as key in dictionary.
            project_number (str): Project number (optional).
            raw_data_path (str): Raw data path (optional).
            absolute_file_path (str): The full absolute file path.
            in_raw_gdb (bool): Indicates whether data is in raw GDB (optional).
            contains_pdf (bool): Indicates whether data contains PDF files (optional).
            contains_image (bool): Indicates whether data contains image files (optional).
            extracted_attachments_path (str): The path to the extracted attachments if applicable (optional).
            processed (bool): Indicates whether data has been processed yet (optional).

        Returns:
            None
        '''
        # Update specified parameters as sets
        project_data = self.data_dict.get(project_spatial_id, {})
        if project_number is not None:
            project_data['project_number'] = project_number
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
        if processed is not None:
            project_data['processed'] = processed
    
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
        
    def find(self, criteria):
        '''
        Find any criteria from the global data class.

        Parameters:
            criteria (dict): A dictionary of criteria of what to search the data class for.

        Returns:
            data_entry: A matching row of the dictionary if the criteria is all returned true, otherwise return None.
        '''        
        #
        return next(
            (
                data_entry
                for data_entry in self.data_dict.values()
                if all(data_entry.get(field) == value for field, value in criteria.items())
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

        return clean_project_number + '_' + str(result_occurrences).zfill(2)
    
    def _load_data(self):
        """
        Load data from an existing data tracker or a database connection into class.

        Returns:
            None
        """
        if self.load_from == 'database':
            # Initialize the connection variable to None
            conn = None
            try:
                # Read connection parameters from the configuration file
                params = config()

                # Connect to the PostgreSQL server using the parameters
                log(None, Colors.INFO, 'Opening connection to the PostgreSQL database...')
                conn = psycopg2.connect(**params)
                
                # Create a cursor to execute SQL queries
                cur = conn.cursor()
                
                # SQL query to retrieve data from the database
                sql = "SELECT project_spatial_id, project_number, project_path, raw_data_path, in_raw_gdb, contains_pdf, contains_image FROM bt_spatial_test.raw_data_tracker;"        

                try:
                    # Execute the SQL query
                    cur.execute(sql)
                    
                    # Fetch all the rows from the result set
                    rows = cur.fetchall()
                    
                    # Initialize an empty dictionary to store the extracted data
                    for row in rows:
                        # Extract the project_spatial_id from the row
                        project_spatial_id = row[0]

                        # Extract the rest of the row values into a dictionary
                        values = {
                            'project_number': row[1],
                            'project_path': row[2],
                            'raw_data_path': row[3],
                            'in_raw_gdb': row[4],
                            'contains_pdf': row[5],
                            'contains_image': row[6]
                        }
                        
                        # Store the values dictionary in the data_dict with project_spatial_id as the key
                        self.data_dict[project_spatial_id] = values
                        
                finally:
                    log(None, Colors.INFO, "Successfully retrieved data from the database.") 

                # close the communication with the PostgreSQL
                cur.close()

            finally:
                if conn is not None:
                    conn.close()
                    log(None, Colors.INFO, 'Database connection closed.') 
        else:    
            # Check to see if the data tracker exists before loading from it
            if not os.path.exists(self.data_tracker):
                raise Exception('Datatracker path that was provided does not exist.')
            
            # Read the data tracker
            data_df = pd.read_excel(self.data_tracker)

            # Use apply with a lambda function to add data to the data_dict
            data_df.apply(lambda row: self.add_data(
                row['project_spatial_id'],
                row['project_number'],
                row['project_path'],
                row['raw_data_path'],
                row['absolute_file_path'],
                row['in_raw_gdb'],
                row['contains_pdf'],
                row['contains_image'],
                row['extracted_attachments_path'],
                row['processed']
            ), axis=1)

    def _save_data(self, save_to='database'):
        """
        Save data tracker information to data tracker or database connection.

        Returns:
            None
        """
        if self.save_to == 'database':            
            # Initialize the connection variable to None
            conn = None
            try:
                # Read connection parameters from the configuration file
                params = config()

                # Connect to the PostgreSQL server using the parameters
                log(None, Colors.INFO, 'Opening connection to the PostgreSQL database...')
                conn = psycopg2.connect(**params)
                
                # Create a cursor to execute SQL queries
                cur = conn.cursor()
                
                # Define the SQL query for inserting data into the database
                sql = "INSERT INTO bt_spatial_test.raw_data_tracker (project_spatial_id, project_number, project_path, raw_data_path, in_raw_gdb, contains_pdf, contains_image) VALUES (%s, %s, %s, %s, %s, %s, %s);"
                
                # Iterate through each key-value pair in the data_dict
                for key, value in self.data_dict.items():
                    # Prepare the parameterized values for the SQL query
                    values = (key, value['project_number'], value['project_path'], value['raw_data_path'], value['in_raw_gdb'], value['contains_pdf'], value['contains_image'])
                    
                    # Check if the key contains the arbitrary project ID 'XXX'; if yes, skip the insertion for that key
                    if 'XXX' in key:
                        log(None, Colors.INFO, f"Skipping key {key} because it contains 'XXX'.")
                        continue
                    else:
                        try:
                            # Execute the SQL query to insert data into the database
                            cur.execute(sql, values)
                            
                            # Commit the changes to the database
                            conn.commit()
                            
                            log(None, Colors.INFO, f"Successfully inserted data for key {key}.")
                        except Exception as e:
                            log(self.log_path, Colors.ERROR, f"Was unable to inser data for {key}: {e}")

                # close the communication with the PostgreSQL
                cur.close()
            except (Exception, psycopg2.DatabaseError) as e:
                log(self.log_path, Colors.ERROR, e)
            finally:
                if conn is not None:
                    conn.close()
                    log(None, Colors.INFO, 'Database connection closed.')   
                
        else: 
            # Create a DataFrame and save it to Excel if the data tracker file doesn't exist
            df = pd.DataFrame(list(self.data_dict.values()), columns=['project_number', 'project_path', 'raw_data_path', 'absolute_file_path', 'in_raw_gdb', 'contains_pdf', 'contains_image', 'extracted_attachments_path', 'processed'])

            # Add 'project_spatial_id' to the DataFrame
            df['project_spatial_id'] = list(self.data_dict.keys())

            # Reorder columns to have 'project_spatial_id' as the first column
            df = df[['project_spatial_id', 'project_number', 'project_path', 'raw_data_path', 'absolute_file_path', 'in_raw_gdb', 'contains_pdf', 'contains_image', 'extracted_attachments_path', 'processed']]

            # Sort the rows by the project_spatial_id column
            df = df.sort_values(by=['project_spatial_id'])
            
            # Check if the directory exists, if not, create it
            directory = os.path.dirname(self.data_tracker)
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Convert dataframe to excel
            df.to_excel(self.data_tracker, index=False)
            
            log(None, Colors.INFO, f'The data tracker "{self.data_tracker}" has been created/updated successfully.')
                