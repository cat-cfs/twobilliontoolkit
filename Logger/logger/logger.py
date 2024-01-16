#========================================================
# Imports
#========================================================
import os
import sys
from datetime import datetime
import inspect

#========================================================
# Global Classes
#========================================================
# ANSI escape codes for colors
class Colors:
    ERROR = '\033[91m' # red
    WARNING = '\033[93m' # yellow
    INFO = '\033[94m' # blue
    END = '\033[0m'
        
#========================================================
# Logger Functions
#========================================================   
def log(file_path=None, type=Colors.ERROR, message=''):
    """
    Log messages with colored tags and timestamps.

    Args:
        file_path (str): Path to the log file.
        type (str): Color code for the log message type.
        message (str): The log message.
        
    Return:
        None.
    """
    # Get the frame of the caller to extract the filepath and linenumber of where log() was called from. Then clean it up.
    frame = inspect.currentframe().f_back
    try:
        filename = frame.f_code.co_filename
        line_number = frame.f_lineno
    finally:
        del frame
    
    # Set the tag
    if type == Colors.INFO:
        tag = 'INFO'
    elif type == Colors.WARNING:
        tag = 'WARNING'
    elif type == Colors.ERROR:
        tag = 'ERROR'
        
    # Print the colored log message to the console
    print(f'{type}[{tag}] {filename}:{line_number} - {message}{Colors.END}')
    
    # If there is a file path provided
    if file_path is not None:
        # Check if the directory exists, if not, create it
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Open the file in append mode and append a log message
        with open(file_path, 'a') as log_file:
            log_file.write(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} [{tag}] {filename}:{line_number} - {message}\n')
    