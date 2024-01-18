# spatial_transformer/config.py
#========================================================
# Imports
#========================================================
from configparser import ConfigParser
import os

#========================================================
# Function
#========================================================
def config(filename=None, section='postgresql'):
    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Join the script directory with the relative path to database.ini
    filename = os.path.join(script_directory, '../database.ini')
       
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