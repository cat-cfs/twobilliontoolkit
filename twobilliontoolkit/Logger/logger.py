#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# twobilliontoolkit/Logger/logger.py
#========================================================
# Created By:       Anthony Rodway
# Email:            anthony.rodway@nrcan-rncan.gc.ca
# Creation Date:    Thur January 18 12:00:00 PST 2024
# Organization:     Natural Resources of Canada
# Team:             Carbon Accounting Team
#========================================================
# File Header
#========================================================
"""
File: twobilliontoolkit/Logger/logger.py
Created By:       Anthony Rodway
Email:            anthony.rodway@nrcan-rncan.gc.ca
Creation Date:    Thur January 18 12:00:00 PST 2024
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    The module holds the function that handles the logging for the package, the user may provide a log path so that each warning and error gets written to that, otherwise everything will be written to the terminal.

Usage:
    Not callable from the command-line
"""

#========================================================
# Imports
#========================================================
import os
import sys
import inspect
from datetime import datetime

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
def log(file_path: str = None, type: str = Colors.ERROR, message: str = '') -> None:
    """
    Log messages with colored tags and timestamps.

    Args:
        file_path (str, optional): Path to the log file.
        type (str): Color code for the log message type.
        message (str): The log message.
    """
    # Get the frame of the caller to extract the filepath and linenumber of where log() was called from. Then clean it up.
    frame = inspect.currentframe().f_back
    try:
        filename = frame.f_code.co_filename
        line_number = frame.f_lineno
    finally:
        del frame
    
    # Set the tag and print to the console
    if type == Colors.INFO:
        tag = 'INFO'
        print(f'{type}[{tag}] {message}{Colors.END}')
    elif type == Colors.WARNING:
        tag = 'WARNING'
        print(f'{type}[{tag}] {filename}:{line_number} - {message}{Colors.END}')
    elif type == Colors.ERROR:
        tag = 'ERROR'
        print(f'{type}[{tag}] {filename}:{line_number} - {message}{Colors.END}')
        
    
    # If a file path is provided
    if file_path is not None:
        # Check if the directory exists, if not, create it
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Open the file in append mode and append a log message
        with open(file_path, 'a') as log_file:
            log_file.write(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} [{tag}] {filename}:{line_number} - {message}\n')
    