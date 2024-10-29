#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# twobilliontoolkit/NetworkTransfer/network_transfer.py
#========================================================
# Created By:       Anthony Rodway
# Email:            anthony.rodway@nrcan-rncan.gc.ca
# Creation Date:    Fri March 29 02:30:00 PST 2024
# Organization:     Natural Resources of Canada
# Team:             Carbon Accounting Team
#========================================================
# File Header
#========================================================
"""
File: twobilliontoolkit/NetworkTransfer/network_transfer.py
Created By:       Anthony Rodway
Email:            anthony.rodway@nrcan-rncan.gc.ca
Creation Date:    Fri March 29 02:30:00 PST 2024
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    A tool to transfer all files or specific files from a source directory to a destination. It is designed to handle the transfer of data, 
    especially for the Two Billion Trees Toolkit processing.


Usage:
    python path/to/network_transfer.py --source <local_path> --destination <network_path> --log <log_file_path> [--ps_script <script_path>] [--files <[...list of files...]>] 

Arguments:
    --source            Path to the source location to transfer files from.
    --destination       Path to the destination location to transfer the files to.
    --log               Path to the log file.
    --ps_script         Optional path to a PowerShell script for additional operations.
    --files             Optional list of files in the source path to transfer over to the destination path.

Example:
    python network_transfer.py --source local/drive/path --destination network/drive/path --log network_transfer.txt --files transfer_file.gdb
"""
#========================================================
# Imports
#========================================================
import os
import sys
import time
import arcpy
import shutil
import argparse
import datetime
 
from twobilliontoolkit.Logger.Logger import Logger

#========================================================
# Entry Function
#========================================================
def network_transfer(local_path: str, network_path: str, logger: Logger, list_files: list[str] = None) -> bool:
    """
    Transfer files from local directory to network directory.
    
    Args:
        local_path (str): Path to the local directory.
        network_path (str): Path to the network directory.
        logger (Logger): The Logger object to store and write to log files and the command line uniformly.
        list_files (list): Optional. A provided list of files to transfew instead of all.
        
    Return:
        (bool): success flag of the operation.
    """
    try:
        if list_files is None:
            # Get list of files and directories in the local directory
            items = os.listdir(local_path)
        else:
            items = list_files
        
        # Iterate over files in the local directory
        for item in items:            
            # Build full paths for source and destination
            src_path = os.path.join(local_path, item)
            dest_path = os.path.join(network_path, item)

            # Skip processing files that do not exist in the source directory
            if not os.path.exists(src_path):
                continue

            # Transfer files or directories
            if os.path.isdir(src_path):
                # Merge Geodatabases if destination exists
                if item.endswith(".gdb"):
                    success = merge_gdbs(src_path, dest_path, logger)
                    if not success:
                        return False
                else:
                    merge_directories(src_path, dest_path, logger)
            else:
                if item.endswith(".txt") and os.path.exists(dest_path):
                    # Append text files if destination file exists
                    with open(dest_path, "a") as dest_file:
                        with open(src_path, "r") as src_file:
                            shutil.copyfileobj(src_file, dest_file)
                else:      
                    shutil.copy2(src_path, dest_path)  # preserves metadata              
                
        logger.log(message=f'The transfer of files has been completed', tag='INFO')
    except Exception as error:
        # Log the exception
        logger.log(message=f'An error has been caught while transferring files from {local_path} to {network_path}: {error}', tag='ERROR')
        return False
    
    return True

#========================================================
# Helper Functions
#========================================================
def merge_gdbs(src_gdb: str, dest_gdb: str, logger: Logger) -> bool:
    """
    Merge source Geodatabase into destination Geodatabase.
 
    Args:
        src_gdb (str): Path to the source Geodatabase.
        dest_gdb (str): Path to the destination Geodatabase.
        logger (Logger): The Logger object to store and write to log files and the command line uniformly.
        
    Return:
        (bool): success flag of the operation.
    """    
    # Set the workplace for the source geodatabase
    arcpy.env.workspace = src_gdb
    try:
        # Copy the whole GDB if it does not exist
        if not arcpy.Exists(dest_gdb):
            if not os.path.exists(os.path.dirname(dest_gdb)):
                os.mkdir(os.path.dirname(dest_gdb))
               
            # Copy over the whole gdb
            arcpy.management.Copy(
                src_gdb,
                dest_gdb
            )
            
            logger.log(message=f'Copy to {dest_gdb} has completed.', tag='INFO')
            return True
           
    except Exception as error:
        logger.log(message=f'An error has been caught while trying to copy the geodatabase to {dest_gdb}: {error}', tag='ERROR')
        return False
       
    # Get a list of feature classes in the source geodatabase
    feature_classes = arcpy.ListFeatureClasses()
    for feature_class in feature_classes:
        try:
            # Skip if already exists in destination
            if arcpy.Exists(os.path.join(dest_gdb, feature_class)):
                continue      
             
            # Copy over the specified feature
            arcpy.management.Copy(
                os.path.join(src_gdb, feature_class),
                os.path.join(dest_gdb, feature_class)
            )            
        except Exception as error:
            # Log the exception
            logger.log(message=f'An error has been caught while trying to merge the geodatabase to {dest_gdb}: {error}', tag='ERROR')
            return False
        
        logger.log(message=f'Merging to {dest_gdb} has completed.', tag='INFO')
        
    return True

def merge_directories(src_dir: str, dst_dir: str, logger: Logger):
    """
    Merge source directory into destination directory.

    Args:
        src_dir (str): Path to the source directory.
        dst_dir (str): Path to the destination directory.
        logger (Logger): The Logger object to store and write to log files and the command line uniformly.
    """
    try:
        if not os.path.exists(dst_dir):
            shutil.copytree(src_dir, dst_dir)
        
        # Iterate over files and subdirectories in the source directory
        for item in os.listdir(src_dir):
            src_item = os.path.join(src_dir, item)
            dst_item = os.path.join(dst_dir, item)

            # If the item is a file, copy it to the destination directory
            if os.path.isfile(src_item):
                shutil.copy2(src_item, dst_item)
                
            # If the item is a directory, recursively merge it with the corresponding directory in the destination
            elif os.path.isdir(src_item):
                merge_directories(src_item, dst_item, logger)
    except Exception as error:
        # Log the exception
        logger.log(message=f'An error has been caught while trying to merge the {src_dir} to {dst_dir}: {error}', tag='ERROR')
                        
#========================================================
# Main
#========================================================
def main():
    """ The main function of the network_transfer.py script """
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='Network Transfer Tool - A tool for transferring all or specific files from a source to a destination directory.')
    
    # Define command-line arguments
    parser.add_argument("--source", type=str, help="Path to the source location to transfer files from.")
    parser.add_argument("--destination", type=str, help="Path to the destination location to transfer the files to.")
    parser.add_argument('--log', required=True, help='Path to the log file.')
    parser.add_argument('--ps_script', default='', help='Optional path to a PowerShell script for additional operations.')
    parser.add_argument("--files", nargs="*", help="Optional list of files in the source path to transfer over to the destination path.")
          
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Initialize the Logger
    logger = Logger(log_file=args.log, script_path=args.ps_script, auto_commit=True, tool_name=os.path.abspath(__file__))
    
    # Get the start time of the script
    start_time = time.time()
    logger.log(message=f'Tool is starting... Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
    
    # Call the entry function
    _ = network_transfer(args.source, args.destination, logger, args.files or None)
    
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