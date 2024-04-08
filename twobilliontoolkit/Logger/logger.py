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
def log(file_path: str = None, type: str = Colors.ERROR, message: str = '', suppress: bool = False, filename: str = None, line_num: int = None) -> None:
    """
    Log messages with colored tags and timestamps.

    Args:
        file_path (str, optional): Path to the log file.
        type (str): Color code for the log message type.
        message (str): The log message.
        suppress (bool, optional): Suppress warnings in the command line.
        filename (str, optional): The filename where the error occured if known.
        line_num (int, optional): The line number in the file that the error occured if known.
    """
    traceback = ''
    if filename and line_num:
        traceback = filename + ' : line:' + str(line_num) + ' - '
        
    # Set the tag and print to the console
    if type == Colors.INFO:
        tag = 'INFO'
        print(f'{type}[{tag}] {message}{Colors.END}')
    elif type == Colors.WARNING and not suppress:
        tag = 'WARNING'
        print(f'{type}[{tag}] {message}{Colors.END}')
    elif type == Colors.WARNING and suppress:
        tag = 'WARNING'
    elif type == Colors.ERROR:
        tag = 'ERROR'
        print(f'{type}[{tag}] {traceback}{message}{Colors.END}')
        
    
    # If a file path is provided
    if file_path is not None:
        # Split the log files into seperate Warning and Error logs
        file_path = r'C:\LocalTwoBillionToolkit\Output\\' + file_path[:-4] + '_' + tag + '.txt'
        
        # Check if the directory exists, if not, create it
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        try:
            # Open the file in append mode and append a log message
            with open(file_path, 'a') as log_file:
                log_file.write(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} [{tag}] {traceback}{message}\n')
        except PermissionError as e:
            print(f"Permission denied to write to file: {file_path}. Error: {e}")
