# SpatialTransformer/Database.py
#========================================================
# Imports
#========================================================
import os
import psycopg2
from configparser import ConfigParser

from twobilliontoolkit.Logger.logger import log, Colors

#========================================================
# Class
#========================================================
class Database:
    """A class for interacting with a PostgreSQL database."""
    
    def __init__(self) -> None:
        """Initialize the Database instance."""
        self.connection = None
        self.cursor = None
    
    def connect(self, params: dict[str, str]) -> None:
        """
        Connect to the database.

        Args:
            params (dict): Dictionary containing database connection parameters.
        """
        try:
            self.connection = psycopg2.connect(**params)
            self.cursor = self.connection.cursor()
            log(None, Colors.INFO, 'Opened a connection to the database...')
        except Exception as error:
            raise Exception(error)
            
    def disconnect(self) -> None:
        """Disconnect from the database."""
        try:
            if self.connection is not None:
                self.connection.close()
                log(None, Colors.INFO, 'Database connection closed.')
        except Exception as error:
            raise Exception(error)
    
    def get_params(self, filename: str = None, section: str = 'postgresql') -> dict[str, str]:
        """
        Get database connection parameters from a configuration file.

        Args:
            filename (str, optional): Path to the configuration file.
            section (str, optional): Section in the configuration file.

        Returns:
            dict: Dictionary containing database connection parameters.
        """
        # Get the directory of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))
        
        # Join the script directory with the relative path to database.ini
        if filename == None:
            filename = os.path.join(script_directory, 'database.ini')
            
            if not os.path.exists(filename):
                raise FileExistsError(f'The database.ini file is not in the correct place/does not exist in {script_directory}')
        
        # create a parser
        parser = ConfigParser()
        
        # read config file
        parser.read(filename)
        
        # get section, default to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                if not param[1]:
                    raise ValueError(f'The [{param[0]}] field in {filename} was not filled out.')
                db[param[0]] = param[1]
        else:
            raise Exception(f'Section {section} not found in the {filename} file')

        return db
                
    def execute(self, query: str, values: list[str] = None) -> None:
        """
        Execute a SQL query.

        Args:
            query (str): SQL query string.
            values (list, optional): List of parameter values for the query.
        """
        self.cursor.execute(query, values)
        self.connection.commit()
          
    def get_columns(self, schema: str, table: str) -> list[str]:
        """
        Get the columns from the table.

        Args:
            schema (str): Name of the database schema.
            table (str): Name of the table.
            
        Returns:
            list: List of strings that correspond to the table columns.
        """
        query = f"SELECT column_name FROM information_schema.columns where CONCAT(table_schema, '.', table_name) = '{schema + '.' + table}'"
        self.execute(query) 
        return [row[0] for row in self.cursor.fetchall()]
            
    def get_pkey(self, schema: str, table: str) -> str:
        """
        Get the primary key from the table.

        Args:
            schema (str): Name of the database schema.
            table (str): Name of the table.
            
        Returns:
            str: The name of the primary key in the schema/table provided.
        """  
        query = f"SELECT * FROM information_schema.key_column_usage where table_schema = '{schema}' and constraint_name = CONCAT('{table}', '_pkey')"
        self.execute(query) 
        return self.cursor.fetchone()
          
    def create(self, schema: str, table: str, columns: list[str], values: list[str]) -> None:
        """
        Insert data into a table.

        Args:
            schema (str): Name of the database schema.
            table (str): Name of the table.
            columns (list): List of column names.
            values (list): List of values to be inserted.
        """
        query = f"INSERT INTO {schema + '.' + table} ({', '.join(columns)}) VALUES ({', '.join(['%s' for _ in values])})"
        self.execute(query, values)
    
    def read(self, schema: str, table: str, columns: list[str] = None, condition: str = None) -> list[tuple]:
        """
        Retrieve data from a table.

        Args:
            schema (str): Name of the database schema.
            table (str): Name of the table.
            columns (list, optional): List of column names to retrieve. Defaults to None (all columns).
            condition (str, optional): SQL condition to filter rows. Defaults to None.

        Returns:
            list: List of tuples containing the retrieved data.
        """
        if columns is None:
            columns = ['*']
        
        query = f"SELECT {', '.join(columns)} FROM {schema + '.' + table}"
        
        if condition is not None:
            query += f" WHERE {condition}"
        
        self.execute(query) 
        
        return self.cursor.fetchall()
    
    def update(self, schema: str, table: str, values_dict: dict[str, str], condition: str) -> None:
        """
        Update data in a table.

        Args:
            schema (str): Name of the database schema.
            table (str): Name of the table.
            values_dict (dict): Dictionary of column-value pairs to be updated.
            condition (str): SQL condition to filter rows to be updated.
        """        
        query = f"UPDATE {schema + '.' + table} SET {', '.join([f'{col}=%s' for col in values_dict.keys()])} WHERE {condition}"
        
        values = list(values_dict.values())
        
        self.execute(query, values)
        
    def delete(self, schema: str, table: str, condition: str) -> None:
        """
        Delete data from a table.

        Args:
            schema (str): Name of the database schema.
            table (str): Name of the table.
            condition (str): SQL condition to filter rows to be deleted.
        """
        query = f"DELETE FROM {schema + '.' + table} WHERE {condition}"
        self.execute(query)
        