#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# geo_attachment_seeker/geo_attachment_seeker.py
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
File: geo_attachment_seeker/geo_attachment_seeker.py
Created By:       Anthony Rodway
Email:            anthony.rodway@nrcan-rncan.gc.ca
Creation Date:    Fri January 05 08:30:00 PST 2024
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    The script identifies and processes attachment tables within the specified GDB, filtering out non-attachment tables. It then extracts attachment files from each table and exports them to a specified output directory. The attachments are exported to a directory structure organized by project IDs. Each attachment file is named with a prefix (e.g., "ATT{attachment_id}_") to distinguish them.

Usage:
    python path/to/geo_attachment_seeker.py gdb_path output_path
"""


#========================================================
# Imports
#========================================================
import os
import sys
import time
import argparse
import arcpy 


#========================================================
# Functions
#========================================================
def find_attachments(gdb_path, output_path):
    '''
    Searches through the gdb and finds all relevant attachments.

    Parameters:
    - gdb_path (str): Path to input GDB.
    - output_path (str): Path to export the attachments to.
    
    Return:
    - attachment_dict (dict): A dictionary of key value pairs to tie each project id that had attachments to the path they were extracted to.
    ''' 
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
        
        # Uncomment following line to print out the names of the _ATTACH Tables in the gdb
        # print(table)
        
        # Build the output project paths
        project_id = table.replace('__ATTACH', '')
        output_project_path = os.path.abspath(os.path.join(output_path, project_id))
        table_path = os.path.join(gdb_path, table)
        
        # Call the processing function
        process_attachment(output_project_path, table_path)
        
        # Add to the dictionary
        attachment_dict[project_id] = output_project_path
           
    # Uncomment following line to print out the resulting dictionary
    # print(attachment_dict)
    
    # Return the attachement dictionary
    return attachment_dict

def process_attachment(output_project_path, table_path):
    '''
    Proccesses any attachments handed to it.

    Parameters:
    - output_project_path (str): The path of where the attachments will be exported.
    - table_path (str): The path to a __ATTACH table in a GDB.
    
    Return:
    - None
    '''                 
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
    # Get the start time of the script
    start_time = time.time()
    print(f'Tool is starting...')
    
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='')
    
    # Define command-line arguments
    parser.add_argument('gdb_path', help='Input GDB path')
    parser.add_argument('output_path', help='Where to export the attachments to')
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the values using the attribute notation
    gdb_path = args.gdb_path
    output_path = args.output_path
    
    # Call the function to perform the processing
    find_attachments(gdb_path, output_path)
        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    print(f'\nTool has completed')
    print(f'Elapsed time: {end_time - start_time:.2f} seconds')


#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    