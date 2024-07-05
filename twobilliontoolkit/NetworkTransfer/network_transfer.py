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
    The script will transfer all files or any files specified from a source directory to a destination. It's main purpose will be used to transfer files from the local computers to a network drive with specific focus on the two billion trees toolkit processing.

Usage:
    python path/to/network_transfer.py local_path source_path network_path destination_path [--files [...list of files...]] 

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
 
from twobilliontoolkit.Logger.logger import log, Colors

#========================================================
# Functions
#========================================================
def merge_gdbs(src_gdb: str, dest_gdb: str, log_path: str = None) -> bool:
    """
    Merge source Geodatabase into destination Geodatabase.
 
    Args:
        src_gdb (str): Path to the source Geodatabase.
        dest_gdb (str): Path to the destination Geodatabase.
        log_path (str): path to the log file.
        
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
            
            log(None, Colors.INFO, f'Copy to {dest_gdb} has completed.')
            return True
           
    except Exception as error:
        log(log_path, Colors.ERROR, f'An error has been caught while trying to copy the geodatabase to {dest_gdb}: {error}')
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
       
            log(None, Colors.INFO, f'Merging to {dest_gdb} has completed.')
        except Exception as error:
            log(log_path, Colors.ERROR, f'An error has been caught while trying to merge the geodatabase to {dest_gdb}: {error}')
            return False
        
    return True

def merge_directories(src_dir, dst_dir, log_path):
    """
    Merge source directory into destination directory.

    Args:
        src_dir (str): Path to the source directory.
        dst_dir (str): Path to the destination directory.
        log_path (str): path to the log file.
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
                merge_directories(src_item, dst_item, log_path)
    except Exception as error:
        log(log_path, Colors.ERROR, f'An error has been caught while trying to merge the {src_dir} to {dst_dir}: {error}')
                        
def transfer(local_path: str, network_path: str, list_files: list[str] = None, log_path: str = None) -> bool:
    """
    Transfer files from local directory to network directory.
    
    Args:
        local_path (str): Path to the local directory.
        network_path (str): Path to the network directory.
        list_files (list): Optional. A provided list of files to transfew instead of all.
        log_path (str): path to the log file.
        
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
                    success = merge_gdbs(src_path, dest_path, log_path)
                    if not success:
                        return False
                else:
                    merge_directories(src_path, dest_path, log_path)
            else:
                if item.endswith(".txt") and os.path.exists(dest_path):
                    # Append text files if destination file exists
                    with open(dest_path, "a") as dest_file:
                        with open(src_path, "r") as src_file:
                            shutil.copyfileobj(src_file, dest_file)
                else:      
                    shutil.copy2(src_path, dest_path)  # preserves metadata              
                
        log(None, Colors.INFO, f'The transfer of files has been completed')
    except Exception as error:
        log(log_path, Colors.ERROR, f'An error has been caught while transferring files from {local_path} to {network_path}: {error}')
        return False
    
    return True

#========================================================
# Main
#========================================================
def main():
    """ The main function of the network_transfer.py script """
    # Get the start time of the script
    start_time = time.time()
    log(None, Colors.INFO, 'Tool is starting...')
    
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description="Transfer files from local to network location")
    parser.add_argument("local_path", type=str, help="Path to the local directory")
    parser.add_argument("network_path", type=str, help="Path to the network directory")
    parser.add_argument("--files", nargs="*", help="Optional. All of the files to transfer to the destination.")
    args = parser.parse_args()
    
    files = args.files or None
    
    # Transfer files
    _ = transfer(args.local_path, args.network_path, files)
    
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, 'Tool has completed')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())