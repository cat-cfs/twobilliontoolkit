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
    This module defines a Logger class that handles logging messages with different severity levels (INFO, WARNING, ERROR) for the TwoBillionToolkit. Users can provide a log file path to store logs, otherwise, logs are written to the terminal. The logger supports features such as separating logs by type, suppressing warnings, auto-committing logs to a file, and including metadata such as tool name and script path.


Usage:
    This module is intended for use within the TwoBillionToolkit and is not callable from the command-line.
"""

#========================================================
# Imports
#========================================================
import os
import datetime
from importlib.metadata import version

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
# Global Constants
#========================================================
LOCAL_DIR = r'C:\LocalTwoBillionToolkit\\'
FILE_EXT = '.txt'    
        
#========================================================
# Class
#========================================================
class Logger:
    """
    A class for logging informational, warning, and error messages to a file or the console.

    This class supports features such as log suppression, automatic file creation, and 
    optional separation of logs by type (INFO, WARNING, ERROR).
    """
    
    def __init__(self, log_file: str, is_absolute_path: bool = True, seperate_logs: bool = False, suppress_warnings: bool = False, script_path: str = 'N/A', auto_commit: bool = False, tool_name: str = None) -> None:
        """
        Initialize a new Logger instance.

        Args:
            log_file (str): Path to the log file. Can be an absolute or relative path.
            is_absolute_path (bool, optional): Determines whether the log file path is absolute. Defaults to True.
            separate_logs (bool, optional): If True, creates separate log files for each log type (INFO, WARNING, ERROR). Defaults to False.
            suppress_warnings (bool, optional): If True, suppresses warnings from being printed to the console. Defaults to False.
            script_path (str, optional): Path to the PowerShell script used to run the spatial transformer. Defaults to 'N/A'.
            auto_commit (bool, optional): If True, logs are automatically written to the file without needing manual commits. Defaults to False.
            tool_name (str, optional): Name of the tool generating the logs. Optional.
        """
        self.created = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        
        self.log_file = log_file
        self.separate_logs = seperate_logs
        self.suppress_warnings = suppress_warnings
        self.script_path = script_path
        self.auto_commit = auto_commit
        self.tool_name = tool_name
        self.log_entries = []  # To store log messages before committing them to file
        self.generated_header = False
        
        if not self.log_file:
            print("Logger Error: No file path provided.")
            exit(0)
        
        if not is_absolute_path:
            self.log_file = LOCAL_DIR + self.log_file[:-4] + FILE_EXT
        
    def log(self, message: str, tag: str = 'ERROR', override: bool = False) -> None:
        """
        Log a message with a specified severity level (ERROR, WARNING, INFO), and store it in memory.

        Args:
            message (str): The message to log.
            tag (str, optional): Severity level of the log message. Can be 'ERROR', 'WARNING', or 'INFO'. Defaults to 'ERROR'.
            override (bool, optional): Override the check of only printing warnings and errors and log info as well. Defaults to False.
        """
        # Set the tag and print to the console
        log_type = self._get_log_type(tag)
                
        # Store the message in the log_entries list
        if tag != 'INFO' or override:
            self.log_entries.append({
                'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'tag': tag,
                'message': message,
                'log_type': log_type
            })
        
        # If suppress is turned on, don't print warnings to command-line
        if tag == 'WARNING' and self.suppress_warnings:
            return
        
        # Print to console immediately
        print(f'{log_type}[{tag}] {message}{Colors.END}')
        
        if self.auto_commit:
            self.commit()
    
    def commit(self, close: bool = False) -> None:
        """
        Write all stored log entries to the designated log file.

        Args:
            close (bool, optional): If True, writes a final closing log entry to the file when a tool completes. Defaults to False.
        """      
        # Iterate through the stored log entries
        for log_entry in self.log_entries:
            tag = log_entry['tag']
            
            # Get the log path
            log_file = self.log_file
            if self.separate_logs:
                log_file = self.log_file[:-4] + f'_{tag}' + FILE_EXT
                
            # Call the function to write to the log file
            self._log_to_file(log_file, log_entry)
            
        # Empty the list of log entries after they have all been written to the file
        self.log_entries = []
        
        # Write closing log for the tool
        if close:
            log_entry = {
                'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'tag': 'INFO',
                'message': f"Tool {self.tool_name} has completed.",
                'log_type': Colors.INFO
            }
            
            # Call the function to write to the log file
            if self.separate_logs:
                self._log_to_file(self.log_file[:-4] + f'_ERROR' + FILE_EXT, log_entry)
                self._log_to_file(self.log_file[:-4] + f'_WARNING' + FILE_EXT, log_entry)
            else:
                self._log_to_file(self.log_file, log_entry)
    
    def _get_tag(self, log_type: str) -> str:
        """
        Determine the tag (INFO, WARNING, ERROR) based on the log type.

        Args:
            log_type (str): The corresponding ANSI color code for the log type.

        Returns:
            str: The severity level of the log (INFO, WARNING, ERROR).
        """
        if log_type == Colors.INFO:
            return 'INFO'
        elif log_type == Colors.WARNING:
            return 'WARNING'
        else:
            return 'ERROR'
        
    def _get_log_type(self, tag: str) -> str:
        """
        Determine the color-coded log type (Colors.INFO, Colors.WARNING, Colors.ERROR) based on the log tag.

        Args:
            tag (str): The severity level of the log (INFO, WARNING, ERROR).

        Returns:
            str: The corresponding ANSI color code for the log type.
        """
        if tag == 'INFO':
            return Colors.INFO
        elif tag == 'WARNING':
            return Colors.WARNING
        else:
            return Colors.ERROR
    
    def _log_to_file(self, log_file: str, log_entry: dict) -> None:
        """
        Write a single log entry to the specified log file.

        Args:
            log_file (str): Path to the log file.
            log_entry (dict): A dictionary containing the log details (timestamp, tag, message, log_type).
        """       
        # Check if the directory exists, if not, create it
        directory = os.path.dirname(log_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Generate header if the file doesn't exist
        if not os.path.exists(log_file) or not self.generated_header:
            self._generate_header(log_file)
            self.generated_header = True
        
        try:
            # Open the file in append mode and write the log entry
            with open(log_file, 'a') as file:
                file.write(f"{log_entry['timestamp']} [{log_entry['tag']}] {log_entry['message']}\n\n")
        except PermissionError as error:
            print(f"Logger Error: Permission denied to write to file {log_file}. Error: {error}\n")
    
    def _generate_header(self, log_file: str,) -> None:
        """
        Generate a header for the log file, containing file metadata and package version.
        
        Args:
            log_file (str): Path to the log file.
        """
        try:
            with open(log_file, 'a') as log_file_o:
                log_file_o.write("___________________________________________________________\n")
                log_file_o.write(f"{os.path.basename(log_file)} file header\n")
                log_file_o.write("___________________________________________________________\n")
                log_file_o.write(f"User: {os.getlogin()}\n")
                log_file_o.write(f"Log Header Created: {self.created} \n")
                log_file_o.write(f"Script Path: {self.script_path}\n")
                log_file_o.write(f"twobilliontoolkit package version: {version('twobilliontoolkit')} \n")
                log_file_o.write("___________________________________________________________\n")
                
                log_file_o.write(f"{self.created} [INFO] Starting tool {self.tool_name}\n\n")
        except Exception as error:
            print(f'An unexpected error occured when creating the log header: {error}\n')
