#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# twobilliontoolkit/RippleUnzipple/ripple_unzipple.py
#========================================================
# Created By:       Anthony Rodway
# Email:            anthony.rodway@nrcan-rncan.gc.ca
# Creation Date:    Fri November 10 14:00:00 PST 2023
# Organization:     Natural Resources of Canada
# Team:             Carbon Accounting Team
#========================================================
# File Header
#========================================================
"""
File: twobilliontoolkit/RippleUnzipple/ripple_unzipple.py
Created By:       Anthony Rodway
Email:            anthony.rodway@nrcan-rncan.gc.ca
Creation Date:    Fri November 10 14:00:00 PST 2023
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    This script recursively extracts all compressed files (.zip and .7z) within a specified input directory or file.
    It can process both individual compressed files and entire directories, creating corresponding output structures.

    - If the input is a directory, the script copies the directory structure to the output location, then unzips all 
      compressed files recursively within the copied directory.
    - If the input is a compressed file (.zip or .7z), it extracts the content directly to the output location.

    Any compressed files within extracted directories are also recursively extracted. The script logs all actions
    to a specified log file, including any errors or issues encountered.

Usage:
    python ripple_unzipple.py --input <input_path> --output <output_path> [--log <log_file_path>] [--ps_script <script_path>]

Arguments:
    --input:        Path to the input directory or compressed file (.zip or .7z).
    --output:       Path to the output directory where extracted files will be saved.
    --log:          Path to the log file.
    --ps_script:    Optional path to a PowerShell script for additional operations.

Examples:
    python ripple_unzipple.py --input /path/to/input --output /path/to/output --log ripple_unzipple.txt
"""

#========================================================
# Imports
#========================================================
import os
import sys
import time
import argparse
import datetime
from zipfile import ZipFile, BadZipFile
from py7zr import SevenZipFile, Bad7zFile
from distutils.dir_util import copy_tree
 
from twobilliontoolkit.Logger.Logger import Logger
  
#========================================================
# Unzipping Functions
#========================================================
def ripple_unzip(input_path: str, output_path: str, logger: Logger) -> None:
    """
    Unzip .zip and .7z files either for a directory or a compressed file.

    Args:
        input_path (str): Path to the input directory or compressed file.
        output_path (str): Path to the output directory.
        logger (Logger): The Logger object to store and write to log files and the command line uniformly.
    """
    try:
        # Check if the provided path exists
        if not os.path.exists(input_path):
            raise ValueError(f"ValueError: The specified path ({input_path}) does not exist")

        # Handle different input extensions
        if os.path.isdir(input_path):
            # First copy the directory to the new location 
            copy_tree(input_path, output_path)
            recursive_unzip(output_path, output_path, logger)
        
        elif input_path.endswith((".zip", ".7z")):
            os.makedirs(output_path, exist_ok=True)

            with ZipFile(input_path, mode='r') if input_path.endswith(".zip") else SevenZipFile(input_path, mode='r') as archive_ref:
                archive_ref.extractall(output_path)
                recursive_unzip(output_path, output_path, input_path, logger)
        
        else:
            raise ValueError("ValueError: Unsupported input type. Please provide a directory or a compressed file.")
        
    except ValueError as error:
        logger.log(message=error, tag='ERROR')
        raise ValueError(error)   
    except Exception as error:
        logger.log(message=error, tag='ERROR')
        raise Exception(error)  
    
def recursive_unzip(input_path: str, output_path: str, original_input_path: str, logger: Logger) -> None:   
    """
    Recursively unzip .zip and .7z files in the input_path to the output_path.

    Args:
        input_path (str): Path to the input directory or compressed file.
        output_path (str): Path to the output directory.
        original_input_path (str): Path of the original input compress/directory.
        logger (Logger): The Logger object to store and write to log files and the command line uniformly.
    """
    # Create output_path if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Iterate through the directory and unzip any compressed folders
    for root, dirs, files in os.walk(input_path):
        for file in files:
            # Get the file path of the input 
            file_path = os.path.join(root, file)
            
            # Make sure that the original zip does not get touched
            if file_path == original_input_path:
                continue

            file_to_remove = ''
            if file.endswith((".zip", ".7z")):
                try:    
                    with ZipFile(file_path, mode='r') if file.endswith(".zip") else SevenZipFile(file_path, mode='r') as archive_ref:
                        # Get the path that the file will be extracted to
                        extract_path = os.path.join(output_path, os.path.splitext(file_path)[0]) 
                        
                        # unzip the file to the location
                        archive_ref.extractall(extract_path)

                        # Recursively call the function to check every file in the directory tree
                        recursive_unzip(extract_path, extract_path, original_input_path, logger)

                        # Flag the compressed file to be removed
                        file_to_remove = extract_path + '.zip' if file.endswith(".zip") else extract_path + '.7z'
                except FileNotFoundError as error:
                    logger.log(message=f"FileNotFoundError: {error.strerror} in ({file_path})\n\nA common cause for this issue may be that the MAX_PATH_LENGTH for your machine's directory is surpassed. The compressed directory will be placed in the folder for you to extract manually. Please read the Configuration section in the README to resolve this issue.", tag='ERROR')
                    continue
                except (BadZipFile, Bad7zFile) as error:
                    logger.log(message=f"BadZipFile or Bad7ZFile: {error.strerror} with ({file_path})\n\nContinuing the tool and placing file for manual extracting.", tag='ERROR')
                    continue

                # Remove the original compressed file from the new output folder
                if os.path.exists(file_to_remove):
                    os.remove(file_to_remove)
  
#========================================================
# Main
#========================================================
def main():
    """ The main function of the ripple_unzipple.py script """
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='Ripple Unzipple Tool - A tool to recursively extract .zip and .7z files, preserving directory structure.')
    
    # Define command-line arguments
    parser.add_argument('--input', required=True, help='Path to the input directory or compressed file (.zip or .7z).')
    parser.add_argument('--output', required=True, help='Path to the output directory where extracted files will be saved.')
    parser.add_argument('--log', default='', help='Path to the log file.')
    parser.add_argument('--ps_script', default='', help='Optional path to a PowerShell script for additional operations.')
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Initialize the Logger
    logger = Logger(log_file=args.log, script_path=args.ps_script, auto_commit=True, tool_name=os.path.abspath(__file__))

    # Get the start time of the script
    start_time = time.time()
    logger.log(message=f'Tool is starting... Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')

    # Call the entry function
    ripple_unzip(args.input, args.output, logger)
        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    logger.log(message=f'Tool has completed. Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
    logger.log(message=f'Elapsed time: {end_time - start_time:.2f} seconds', tag='INFO')
    
    # Commit all messages that have been posted to logger
    logger.commit(close=True)

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    