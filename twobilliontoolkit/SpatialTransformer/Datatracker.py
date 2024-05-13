# twobilliontoolkit/SpatialTransformer/Datatracker.py
#========================================================
# Imports
#========================================================
import psycopg2

from twobilliontoolkit.SpatialTransformer.common import *
from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.SpatialTransformer.Database import Database

#========================================================
# Base Class
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
        self.datatracker = data_traker_path
        self.load_from = load_from
        self.save_to = save_to
        self.log_path = log_path
        
        if load_from == 'database' or save_to == 'database':
            # Create database object
            self.database_connection = Database()
            
            # Read connection parameters from the configuration file
            self.database_parameters = self.database_connection.get_params()
            self.database_connection.connect(self.database_parameters)
            self.database_pkey = self.database_connection.get_pkey(self.database_connection.schema, self.database_connection.table)
            self.database_connection.disconnect()
        
        self.load_data()
    
    def add_data(self, key: str, **kwargs) -> None:
        """
        Adds project data to the data tracker.

        Args:
            key (str): Acts as key in dictionary.
            **kwargs: Additional keyword arguments for project data.
        """
        self.data_dict[key] = kwargs
        
    def set_data(self, key: str, **kwargs) -> None:
        """
        Updates project data in the data tracker.

        Args:
            key (str): Acts as key in dictionary.
            **kwargs: Keyword arguments for updating project data.
        """
        # Update specified parameters as sets
        project_data = self.data_dict.get(key, {})
        
        for pkey, pvalue in kwargs.items():
            if pvalue is not None:
                project_data[pkey] = pvalue
        
        self.data_dict[key] = project_data
    
    def get_data(self, key: str) -> dict:
        """
        Gets an object of values given a project spatial id.

        Args:
            key (str): Acts as key in dictionary.

        Returns:
            dict: the values that correspond to the given key
        """
        return self.data_dict[key]
    
    def find_matching_data(self, **kwargs) -> (str, dict): # type: ignore
        """
        Search for a matching entry in the data based on given parameters.

        Args:
            **kwargs: Keyword arguments for finding a matching key.

        Returns:
            str: A tuple of matching (key, data) if  the parameters passed already exists in the dataframe, otherwise return None.
        """        
        return next(
            (
                (key, data)
                for key, data in self.data_dict.items()
                if all(data.get(field) == value for field, value in kwargs.items())
            ),
            (None, None)
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
            1 for data in self.data_dict.values() if data.get(field) == value
        )

    def load_data(self) -> None:
        """
        Load data from an existing data tracker or a database connection into class.
        """
        if self.load_from == 'database':
            self.load_from_database()
        else:
            self.load_from_file()

    def load_from_database(self) -> None:
        """
        Load data from a database connection into class.
        """
        self.database_connection.connect(self.database_parameters)

        columns = self.database_connection.get_columns(schema=self.database_connection.schema, table=self.database_connection.table)
        
        rows = self.database_connection.read(schema=self.database_connection.schema, table=self.database_connection.table, columns=columns)
        
        for fields in rows:
            values = dict(zip(columns[1:], fields[1:]))
            self.data_dict[self.database_pkey] = values

        self.database_connection.disconnect()

    def load_from_file(self) -> None:
        """
        Load data from a file into class.
        """
        if not os.path.exists(self.datatracker):
            return

        data_df = pd.read_excel(self.datatracker)

        for index, row in data_df.iterrows():
            pkey = row.index[0]
            data = row.drop(pkey).to_dict()
            self.add_data(key=row[pkey], **data)
            
    def save_data(self, update: bool = False) -> None:
        """
        Save data tracker information to data tracker or database connection.

        Args:
            update (bool): Flag to determine if there are some entries in the data object that will need updating.
        """
        if self.save_to == 'database':
            self.save_to_database(update)
        else:
            self.save_to_file()

    def save_to_database(self, update: bool = False) -> None:
        """
        Save data tracker information to a database connection.

        Args:
            update (bool): Flag to determine if there are some entries in the data object that will need updating.
        """
        self.database_connection.connect(self.database_parameters)

        existing_keys = set(row[0] for row in self.database_connection.read(
            schema=self.database_connection.schema, 
            table=self.database_connection.table, 
            columns=[self.database_pkey]
        ))

        for key, value in self.data_dict.items():
            if key in existing_keys and update:
                self.database_connection.update(
                    schema=self.database_connection.schema, 
                    table=self.database_connection.table,
                    values_dict={field: value[field] for field in value},
                    condition=f"{self.database_pkey}='{key}'"
                )
            elif key not in existing_keys:
                self.database_connection.create(
                    schema=self.database_connection.schema, 
                    table=self.database_connection.table,
                    columns=[self.database_pkey] + list(value.keys()),
                    values=[key] + list(value.values())
                )

        self.database_connection.disconnect()

    def save_to_file(self) -> None:
        """
        Save data tracker information to a file.
        """
        df = pd.DataFrame(list(self.data_dict.values()))
        df.insert(0, 'key', self.data_dict.keys())

        if not df.empty:
            df.to_excel(self.datatracker, index=False)
            log(None, Colors.INFO, f'The data tracker "{self.datatracker}" has been created/updated successfully.')
    
         
#========================================================
# Inheritance Class
#========================================================
class Datatracker2BT(Datatracker):
    def __init__(self, data_traker_path: str, load_from: str = 'database', save_to: str = 'database', log_path: str = None) -> None:
        """
        Initializes the Data class with input parameters. Used to store the data tracker information.

        Args:
            data_traker_path (str): Path to data tracker to load data if exists.
            load_from (str): Flag to determine if loading dataframe should be done from the {database, datatracker}. Default: 'database'.
            save_to (str): Flag to determine if saving the dataframe should be done to the {database, datatracker}. Default: 'database'.
            log_path (str, optional): The path to the log file if you wish to keep any errors that occur.
        """
        super().__init__(data_traker_path, load_from, save_to, log_path)
    
    def add_data(self, project_spatial_id: str, project_number: str, dropped: bool, raw_data_path: str, raw_gdb_path: str, absolute_file_path: str, in_raw_gdb: bool, contains_pdf: bool, contains_image: bool, extracted_attachments_path: str, editor_tracking_enabled: bool, processed: bool, entry_type: str) -> None:
        """
        Adds project data to the data tracker.

        Args:
            project_spatial_id (str): Project spatial ID. Acts as key in dictionary.
            project_number (str): Project number.
            dropped (bool): Indicates whether the entry is dropped, non-valid etc.
            raw_data_path (str): Raw data path.
            raw_gdb_path (str): Absolute path to the output geodatabase.
            absolute_file_path (str): The full absolute file path.
            in_raw_gdb (bool): Indicates whether data is in raw GDB.
            contains_pdf (bool): Indicates whether data contains PDF files.
            contains_image (bool): Indicates whether data contains image files.
            extracted_attachments_path (str): The path to the extracted attachments if applicable.
            editor_tracking_enabled (bool): Indicates whether the editor tracking has been enabled for the layer in the gdb.
            processed (bool): Indicates whether data has been processed yet.
            entry_type (str): Indicates wether the entry contains information for an aspatial or spatial entry.
        """
        self.data_dict[project_spatial_id] = {
            'project_number': project_number,
            'dropped': dropped,
            'raw_data_path': raw_data_path,
            'raw_gdb_path': raw_gdb_path,
            'absolute_file_path': absolute_file_path,
            'in_raw_gdb': in_raw_gdb,
            'contains_pdf': contains_pdf,
            'contains_image': contains_image,
            'extracted_attachments_path': extracted_attachments_path,
            'editor_tracking_enabled': editor_tracking_enabled,
            'processed': processed,
            'entry_type': entry_type
        }
        
    def set_data(self, project_spatial_id: str, project_number: str = None, dropped: bool = None, raw_data_path: str = None, absolute_file_path: str = None, in_raw_gdb: bool = None, contains_pdf: bool = None, contains_image: bool = None, extracted_attachments_path: str = None, editor_tracking_enabled: bool = None, processed: bool = None, entry_type: str = None) -> None:
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
            entry_type (str): Indicates wether the entry contains information for an aspatial or spatial entry (optional).
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
        if entry_type is not None:
            project_data['entry_type'] = entry_type
            
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
    
    def load_from_database(self) -> None:
        """
        Load data from a database connection into class.
        """
        self.database_connection.connect(self.database_parameters)

        columns = ['project_spatial_id', 'project_number', 'dropped', 'raw_data_path','raw_gdb_path','absolute_file_path', 'in_raw_gdb', 'contains_pdf', 'contains_image','extracted_attachments_path', 'editor_tracking_enabled', 'processed', 'entry_type']

        rows = self.database_connection.read(schema=self.database_connection.schema, table=self.database_connection.table, columns=columns)

        for fields in rows:
            project_spatial_id = fields[0]
            values = dict(zip(columns[1:], fields[1:]))
            self.data_dict[project_spatial_id] = values

        self.database_connection.disconnect()

    def load_from_file(self) -> None:
        """
        Load data from a file into class.
        """
        if not os.path.exists(self.datatracker):
            return
        
        data_df = pd.read_excel(self.datatracker, dtype={
            'project_spatial_id': object, 
            'project_number': object,
            'dropped': bool, 
            'raw_data_path': object, 
            'raw_gdb_path': object,
            'absolute_file_path': object,
            'in_raw_gdb': bool, 
            'contains_pdf': bool,
            'contains_image': bool, 
            'extracted_attachments_path': object,
            'editor_tracking_enabled': bool, 
            'processed': bool, 
            'entry_type': str
        }, index_col=None)
        
        for index, row in data_df.iterrows():
            self.add_data(
                project_spatial_id=row['project_spatial_id'],
                project_number=row['project_number'], 
                dropped=row['dropped'],
                raw_data_path=row['raw_data_path'], 
                raw_gdb_path=row['raw_gdb_path'], 
                absolute_file_path=row['absolute_file_path'],
                in_raw_gdb=row['in_raw_gdb'], 
                contains_pdf=row['contains_pdf'], 
                contains_image=row['contains_image'],
                extracted_attachments_path=row['extracted_attachments_path'],
                editor_tracking_enabled=row['editor_tracking_enabled'],
                processed=row['processed'], 
                entry_type=row['entry_type']
            )
                    
    def save_to_database(self, update: bool = False) -> None:
        """
        Save data tracker information to a database connection.

        Args:
            update (bool): Flag to determine if there are some entries in the data object that will need updating.
        """
        self.database_connection.connect(self.database_parameters)
        
        rows = self.database_connection.read(
            schema=self.database_connection.schema, 
            table=self.database_connection.table,
            columns=['project_spatial_id']
        )
        existing_ids = set(row[0] for row in rows)

        for key, value in self.data_dict.items():
            try:
                if key in existing_ids and update:
                    self.database_connection.update(
                        schema=self.database_connection.schema, 
                        table=self.database_connection.table,
                        values_dict={
                            'dropped': value['dropped'],
                            'in_raw_gdb': value['in_raw_gdb'], 
                            'contains_pdf': value['contains_pdf'], 
                            'contains_image': value['contains_image'],
                            'editor_tracking_enabled': value['editor_tracking_enabled'], 
                            'processed': value['processed'], 'entry_type': value['entry_type']
                        },
                        condition=f"project_spatial_id='{key}'"
                    )
                    
                elif key not in existing_ids:
                    self.database_connection.create(
                        schema=self.database_connection.schema, 
                        table=self.database_connection.table,
                        columns=('project_spatial_id', 'project_number', 'dropped', 'raw_data_path', 'raw_gdb_path', 'absolute_file_path', 'in_raw_gdb', 'contains_pdf', 'contains_image', 'extracted_attachments_path', 'editor_tracking_enabled', 'processed', 'entry_type'),
                        values=(
                            key, 
                            value['project_number'], 
                            value['dropped'], 
                            value['raw_data_path'],
                            value['raw_gdb_path'], 
                            value['absolute_file_path'], 
                            value['in_raw_gdb'], 
                            value['contains_pdf'], 
                            value['contains_image'],
                            value['extracted_attachments_path'],
                            value['editor_tracking_enabled'],
                            value['processed'], 
                            value['entry_type']
                        )
                    ) 
                    
            except psycopg2.errors.ForeignKeyViolation as error:
                log(self.log_path, Colors.ERROR, error)
            
        self.database_connection.disconnect()

    def save_to_file(self) -> None:
        """
        Save data tracker information to a file.
        """
        # TODO: Work on getting the save to file exactly like save to database
        
        # Create a DataFrame and save it to Excel if the data tracker file doesn't exist
        df = pd.DataFrame(list(self.data_dict.values()), columns=['project_number', 'dropped', 'raw_data_path', 'raw_gdb_path', 'absolute_file_path', 'in_raw_gdb', 'contains_pdf', 'contains_image', 'extracted_attachments_path', 'editor_tracking_enabled', 'processed', 'entry_type'])

        # Add 'project_spatial_id' to the DataFrame
        df['project_spatial_id'] = list(self.data_dict.keys())

        # Reorder columns to have 'project_spatial_id' as the first column
        df = df[['project_spatial_id', 'project_number', 'dropped', 'raw_data_path', 'raw_gdb_path', 'absolute_file_path', 'in_raw_gdb', 'contains_pdf', 'contains_image', 'extracted_attachments_path', 'editor_tracking_enabled', 'processed', 'entry_type']]

        # Sort the rows by the project_spatial_id column
        df = df.sort_values(by=['project_spatial_id'])
        
        # Check if the directory exists, if not, create it
        directory = os.path.dirname(self.datatracker)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Convert dataframe to excel
        df.to_excel(self.datatracker, index=False)
        
        log(None, Colors.INFO, f'The data tracker "{self.datatracker}" has been created/updated successfully.')