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
    Recursively unzips all compressed folders in a given directory.

Usage:
    python ripple_unzipple.py input_path output_path [log_path]
"""

#========================================================
# Imports
#========================================================
import os
import sys
import time
import argparse
from datetime import datetime
from zipfile import ZipFile, BadZipFile
from py7zr import SevenZipFile, Bad7zFile
from distutils.dir_util import copy_tree
 
from twobilliontoolkit.Logger.logger import log, Colors
  
#========================================================
# Unzipping Functions
#========================================================
def ripple_unzip(input_path: str, output_path: str, log_path: str = '') -> None:
    """
    Unzip .zip and .7z files either for a directory or a compressed file.

    Args:
        input_path (str): Path to the input directory or compressed file.
        output_path (str): Path to the output directory.
        log_path (str, optional): Path to the log file. Defaults to ''.
    """
    try:
        # Check if the provided path exists
        if not os.path.exists(input_path):
            raise ValueError(f"ValueError: The specified path ({input_path}) does not exist")

        # Handle different input extensions
        if os.path.isdir(input_path):
            # First copy the directory to the new location 
            copy_tree(input_path, output_path)
            recursive_unzip(output_path, output_path, log_path)
        
        elif input_path.endswith((".zip", ".7z")):
            os.makedirs(output_path, exist_ok=True)

            with ZipFile(input_path, mode='r') if input_path.endswith(".zip") else SevenZipFile(input_path, mode='r') as archive_ref:
                archive_ref.extractall(output_path)
                recursive_unzip(output_path, output_path, input_path, log_path)
        
        else:
            raise ValueError("ValueError: Unsupported input type. Please provide a directory or a compressed file.")
        
    except ValueError as error:
        log(log_path, Colors.ERROR, error)
        raise ValueError(error)   
    except Exception as error:
        log(log_path, Colors.ERROR, error)
        raise Exception(error)  
    
def recursive_unzip(input_path: str, output_path: str, original_input_path: str, log_path: str = '') -> None:   
    """
    Recursively unzip .zip and .7z files in the input_path to the output_path.

    Args:
        input_path (str): Path to the input directory or compressed file.
        output_path (str): Path to the output directory.
        original_input_path (str): Path of the original input compress/directory.
        log_path (str, optional): Path to the log file. Defaults to ''.
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
                        recursive_unzip(extract_path, extract_path, original_input_path, log_path)

                        # Flag the compressed file to be removed
                        file_to_remove = extract_path + '.zip' if file.endswith(".zip") else extract_path + '.7z'
                except FileNotFoundError as error:
                    error_message = f"FileNotFoundError: {error.strerror} in ({file_path})\n\nA common cause for this issue may be that the MAX_PATH_LENGTH for your machine's directory is surpassed. The compressed directory will be placed in the folder for you to extract manually. Please read the Configuration section in the README to resolve this issue."
                    log(log_path, Colors.ERROR, error_message)
                    continue
                except (BadZipFile, Bad7zFile) as error:
                    error_message = f"BadZipFile or Bad7ZFile: {error.strerror} with ({file_path})\n\nContinuing the tool and placing file for manual extracting."
                    log(log_path, Colors.ERROR, error_message)
                    continue

                # Remove the original compressed file from the new output folder
                if os.path.exists(file_to_remove):
                    os.remove(file_to_remove)
  
#========================================================
# Main
#========================================================
def main():
    """ The main function of the ripple_unzipple.py script """
    # Get the start time of the script
    start_time = time.time()
    log(None, Colors.INFO, 'Tool is starting...')
    
    parser = argparse.ArgumentParser(description='Recursively unzip all compressed folders in a given directory.')
    parser.add_argument('--input', required=True, help='Path to the input directory or compressed file.')
    parser.add_argument('--output', required=True, help='Path to the output directory.')
    parser.add_argument('--log', default='', help='Path to the log file.')

    args = parser.parse_args()

    try:
        ripple_unzip(args.input, args.output, args.log)
    except Exception as error:
        log(args.log, Colors.ERROR, error)
        exit(1)
        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, 'Tool has completed')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    