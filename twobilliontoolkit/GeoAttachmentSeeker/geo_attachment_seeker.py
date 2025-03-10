#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# twobilliontoolkit/GeoAttachmentSeeker/geo_attachment_seeker.py
#========================================================
# Created By:       Anthony Rodway
# Email:            anthony.rodway@nrcan-rncan.gc.ca
# Creation Date:    Fri January 05 08:30:00 PST 2024
# Organization:     Natural Resources of Canada
# Team:             Carbon Accounting Team
#========================================================
# File Header
#========================================================
"""
File: twobilliontoolkit/GeoAttachmentSeeker/geo_attachment_seeker.py
Created By:       Anthony Rodway
Email:            anthony.rodway@nrcan-rncan.gc.ca
Creation Date:    Fri January 05 08:30:00 PST 2024
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    A tool to identify and process attachment tables within the specified GDB, filtering out non-attachment tables. It extracts 
    attachment files from each table and exports them to a specified output directory. Attachments are organized by project IDs and 
    exported with a prefix (e.g., "ATT{attachment_id}_") to distinguish them.

Usage:
    python path/to/geo_attachment_seeker.py --gdb <gdb_path> --output <output_path> --log <log_file_path> [--ps_script <script_path>]

Arguments:
    --gdb           Path to the input GDB.
    --output        Path to the directory where attachments will be exported.
    --log           Path to the log file.
    --ps_script     Optional path to a PowerShell script for additional operations.

Example:
    python geo_attachment_seeker.py --gdb my_geodatabase.gdb --output output_dir --log geo_attachment_seeker.txt
"""

#========================================================
# Imports
#========================================================
import os
import sys
import time
import arcpy
import argparse
import datetime
 
from twobilliontoolkit.Logger.Logger import Logger

#========================================================
# Functions
#========================================================
def find_attachments(gdb_path: str, output_path: str) -> dict:
    """
    Searches through the GDB and finds all relevant attachments.

    Args:
        gdb_path (str): Path to input GDB.
        output_path (str): Path to export the attachments to.

    Returns:
        dict: A dictionary of key-value pairs tying each project ID that had attachments to the path they were extracted to.
    """ 
    # validate the gdb_path
    if not isinstance(gdb_path, str) or not gdb_path.strip():
        raise ValueError(f'The provided gdb_path must be a non-empty string.')

    if not gdb_path.endswith('.gdb'):
        raise ValueError(f'The provided gdb_path must be of type ".gdb".')

    if not os.path.exists(gdb_path):
        raise ValueError(f'The provided gdb_path path does not exist.')
    
    # Set the arc environment
    arcpy.env.workspace = gdb_path
    
    # Work all attach tables
    attachment_dict = {}
    for table in arcpy.ListTables(): 
        # Filter out non attachment tables   
        if '__ATTACH' not in table:
            continue
        
        # Build the output project paths
        project_id = table.replace('__ATTACH', '')
        output_project_path = os.path.abspath(os.path.join(output_path, project_id))
        table_path = os.path.join(gdb_path, table)
        
        # Call the processing function
        process_attachment(output_project_path, table_path)
        
        # Add to the dictionary
        attachment_dict[project_id] = output_project_path
            
    # Return the attachement dictionary
    return attachment_dict

def process_attachment(output_project_path: str, table_path : str) -> None:
    """
    Processes any attachments handed to it.

    Args:
        output_project_path (str): The path where the attachments will be exported.
        table_path (str): The path to a __ATTACH table in a GDB.
    """                
    # Check if the directory exists, if not, create it
    if not os.path.exists(output_project_path):
        os.makedirs(output_project_path)
    
    # Extract the attachment files from each table
    # Credits: A Modified version of the method Andrea found at https://support.esri.com/en-us/knowledge-base/how-to-batch-export-attachments-from-a-feature-class-in-000011912
    with arcpy.da.SearchCursor(table_path, ['DATA', 'ATT_NAME', 'ATTACHMENTID']) as cursor:
        for attachment, att_name, attachment_id in cursor:
            filenum = f"ATT{attachment_id}_"
            filename = os.path.join(output_project_path, filenum + att_name)
            
            with open(filename, 'wb') as file:
                file.write(attachment.tobytes())
            
#========================================================
# Main
#========================================================
def main():#
    """ The main function of the geo_attachment_seeker.py script """
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='GeoAttachment Seeker Tool - A tool to extract attachment files from GDB attachment tables and export them to a specified directory.')
    
    # Define command-line arguments
    parser.add_argument('--gdb', help='Path to the input GDB.')
    parser.add_argument('--output', help='Path to the directory where attachments will be exported.')
    parser.add_argument('--log', required=True, help='Path to the log file.')
    parser.add_argument('--ps_script', default='', help='Optional path to a PowerShell script for additional operations.')
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Initialize the Logger
    logger = Logger(log_file=args.log, script_path=args.ps_script, auto_commit=True, tool_name=os.path.abspath(__file__))
    
    # Get the start time of the script
    start_time = time.time()
    logger.log(message=f'Tool is starting... Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
    
    # Call the function to perform the processing
    find_attachments(args.gdb, args.output)
        
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
    