# SpatialTransformer/database_connection.py
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
class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self, params):
        # try:
        self.connection = psycopg2.connect(**params)
        self.cursor = self.connection.cursor()
        log(None, Colors.INFO, 'Opened a connection to the database...')
        # except (Exception, psycopg2.DatabaseError) as error:
            # log(log_file, Colors.ERROR, error)
            
    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            log(None, Colors.INFO, 'Database connection closed.')
    
    def get_params(self, filename=None, section='postgresql'):
        # Get the directory of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))
        
        # Join the script directory with the relative path to database.ini
        if filename == None:
            filename = os.path.join(script_directory, 'database.ini')
        
        # create a parser
        parser = ConfigParser()
        
        # read config file
        parser.read(filename)

        # get section, default to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception(f'Section {section} not found in the {filename} file')

        return db
                
    def execute(self, query, values=None):
        # try:
        self.cursor.execute(query, values)
        self.connection.commit()
        # except Exception as error:
            # log(log_file, Colors.ERROR, error)s
            
    def create(self, table, columns, values):
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s' for _ in values])})"
        self.execute(query, values)
    
    def read(self, table, columns=None, condition=None):
        if columns is None:
            columns = ['*']
            
        query = f"SELECT {', '.join(columns)} FROM {table}"
        
        if condition is not None:
            query += f" WHERE {condition}"
        
        self.execute(query) 
        
        return self.cursor.fetchall()
    
    def update(self, table, values_dict, condition):
        query = f"UPDATE {table} SET {', '.join([f'{col}=%s' for col in values_dict.keys()])} WHERE {condition}"
        
        values = list(values_dict.values())
        
        self.execute(query, values)
        
    def delete(self, table, condition):
        query = f"DELETE FROM {table} WHERE {condition}"
        self.execute(query)
        
    
        