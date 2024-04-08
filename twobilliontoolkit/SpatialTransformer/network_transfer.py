#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# twobilliontoolkit/SpatialTransformer/network_transfer.py
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
File: twobilliontoolkit/SpatialTransformer/network_transfer.py
Created By:       Anthony Rodway
Email:            anthony.rodway@nrcan-rncan.gc.ca
Creation Date:    Fri March 29 02:30:00 PST 2024
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    The script will transfer all files or any files specified from a source directory to a destination. It's main purpose will be used to transfer files from the local computers to a network drive with specific focus on the two billion trees toolkit processing.

Usage:
    python path/to/network_transfer.py <local_path> <network_path> [--gdb_filename GDB_FILENAME] [--log_filename LOG_FILENAME] [--datatracker_filename DATATRACKER_FILENAME]

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
def merge_gdbs(src_gdb: str, dest_gdb: str, log_path: str = None) -> None:
    """
    Merge source Geodatabase into destination Geodatabase.

    Args:
        src_gdb (str): Path to the source Geodatabase.
        dest_gdb (str): Path to the destination Geodatabase.
        log_path (str): path to the log file.
    """
    try:
        # Set the workplace for the source geodatabase
        arcpy.env.workspace = src_gdb
        
        # Get a list of feature classes in the source geodatabase
        feature_classes = arcpy.ListFeatureClasses()
        for feature_class in feature_classes:
            # Skip if already exists in destination
            if arcpy.Exists(os.path.join(dest_gdb, feature_class)):
                continue
                        
            arcpy.management.Copy(
                os.path.join(src_gdb, feature_class),
                os.path.join(dest_gdb, feature_class)
            )
        
        log(None, Colors.INFO, f'Merging to {dest_gdb} has completed.')
    except Exception as error:
        log(log_path, Colors.ERROR, f'An error has been caught while trying merge the geodatabase to {dest_gdb}: {error}\n')

def safe_copy(file_path: str, out_dir: str, dst: str = None):
    """
    Safely copy the specified directory. If a directory with the 
    same name already exists, the copied directory name is altered to preserve both.

    Args
        file_path (str): Path to the directory to copy.
        out_dir (str): Directory to copy.
        dst (str): New name for the copied directory. If None, use 
        the name of the original directory. 
    """
    # Get the base name of the directory
    name = dst or os.path.basename(file_path)
    
    # If directory doesn't exist in the destination, simply copy it
    if not os.path.exists(os.path.join(out_dir, name)):
        shutil.copytree(file_path, os.path.join(out_dir, name))
    else:
        # If directory with the same name already exists, append _1, _2, ... to the copied directory name
        base, extension = os.path.splitext(name)
        i = 1
        while os.path.exists(os.path.join(out_dir, '{}_{}.{}'.format(base, i, extension))):
            i += 1
        shutil.copytree(file_path, out_dir + '{}_{}{}'.format(base, i, 
        extension))
                
def transfer(local_path: str, network_path: str, list_files: list[str] = None, log_path: str = None) -> None:
    """
    Transfer files from local directory to network directory.
    
    Args:
        local_path (str): Path to the local directory.
        network_path (str): Path to the network directory.
        list_files (list): Optional. A provided list of files to transfew instead of all.
        log_path (str): path to the log file.
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
            
            # Transfer files or directories
            if os.path.isdir(src_path):
                # Merge Geodatabases if destination exists
                if item.endswith(".gdb") and os.path.exists(dest_path):
                    merge_gdbs(src_path, dest_path, log_path)
                else:
                    # Use safe_copy to copy directories
                    safe_copy(src_path, network_path)
            else:
                shutil.copy2(src_path, dest_path)  # preserves metadata              
                
        log(None, Colors.INFO, f'The transfer of files has been completed')
    except Exception as error:
        log(log_path, Colors.ERROR, f'An error has been caught while transfering files from {local_path} to {network_path}: {error}\n')

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
    transfer(args.local_path, args.network_path, files)
    
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, 'Tool has completed')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())