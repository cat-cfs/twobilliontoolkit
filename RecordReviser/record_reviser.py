#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# record_reviser/record_reviser.py
#========================================================
# Created By:       Anthony Rodway
# Email:            anthony.rodway@nrcan-rncan.gc.ca
# Creation Date:    Wed January 17 10:30:00 PST 2024
# Organization:     Natural Resources of Canada
# Team:             Carbon Accounting Team
#========================================================
# File Header
#========================================================
"""
File: geo_attachment_seeker/geo_attachment_seeker.py
Created By:       Anthony Rodway
Email:            anthony.rodway@nrcan-rncan.gc.ca
Creation Date:    Wed January 17 10:30:00 PST 2024
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    The script 

Usage:
    python path/to/
"""

#========================================================
# Imports
#========================================================
import os
import sys
import time
import argparse
import tkinter as tk
from tkinter import messagebox

# Additional import for Dash
import dash
from dash import html
import webbrowser

from Logger.logger import log, Colors

# from Logger.logger.logger import log, Colors
# from toolkit2bt.SpatialTransformer.spatial_transformer.DataTrackerModule import DataTracker


#========================================================
# Functions
#========================================================

def create_duplicate():
    pass

def update_record():
    pass

def open_dash_table(data):
    """Open Dash table in the browser."""
    app = dash.Dash(__name__)
    
    # Dash app layout with an editable table
    app.layout = html.Div([
        dcc.Input(id='table-data', type='text', value=str(data)),
        dcc.Datatable(
            id='editable-table',
            editable=True,
            columns=[{'name': 'Column {}'.format(i), 'id': 'column_{}'.format(i)} for i in range(len(data[0]))],
            data=[{f'column_{i}': row[i] for i in range(len(data[0]))} for row in data],
        ),
    ])
    
    # Run Dash app
    app.run_server(debug=True, use_reloader=False)
    print('tetststs')

def confirm_and_open_dash_table(data):
    """Ask user for confirmation before opening Dash table."""
    confirmed = messagebox.askyesno("Confirm", "Do you want to open the table with Dash?")
    if confirmed:
        try:
            # Attempt to open Dash app in the default web browser
            webbrowser.open("http://localhost:8050/", new=2, autoraise=True)
            
            open_dash_table(data)
        except Exception as e:
            # Handle any exceptions that may occur
            messagebox.showerror("Error", f"Failed to open Dash app: {e}")


#========================================================
# Main
#========================================================
def main():#
    """ The main function of the record_reviser.py script """
    # Get the start time of the script
    start_time = time.time()
    log(None, Colors.INFO, 'Tool is starting...')
    
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='')
    
    # Define command-line arguments
    # parser.add_argument('--gdb', required=True, default='', help='The new location or where an exsiting Geodatabase is located')
    parser.add_argument('--load', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to load from (datatracker or database)')
    parser.add_argument('--save', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to save to (datatracker or database)')
    parser.add_argument('--data_tracker', default=None, help='The new location or where an exsiting data tracker is located')
    parser.add_argument('--log', default=None, help='The new location or where an existing log file is located (optional)')
    
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the values using the attribute notation
    # gdb_path = args.gdb
    data_tracker_path = args.data_tracker
    load_from = args.load
    save_to = args.save
    log_path = args.log
    
    # Ensure that if a datatracker is specified for loading or saving, then a path must be passed
    if (load_from == 'datatracker' or save_to == 'datatracker') and data_tracker_path == None:
        raise argparse.ArgumentTypeError("If --load or --save is 'datatracker', --data_tracker_path must be specified.")
    elif (load_from == 'datatracker' or save_to == 'datatracker') and data_tracker_path != None:
        if not isinstance(data_tracker_path, str) or not data_tracker_path.strip():
            raise ValueError(f'data_tracker_path: {data_tracker_path} must be a non-empty string.')
        if not data_tracker_path.endswith('.xlsx'):
            raise ValueError(f'data_tracker_path: {data_tracker_path} must be of type .xlsx.')
        if not os.path.exists(data_tracker_path):
            raise ValueError(f'data_tracker_path: {data_tracker_path} path does not exist.')
    
    data = DataTracker(data_traker_path, load_from, save_to, log_path)
    
    # Call the function to perform the processing
    update_record(data)
    
    # Ask for confirmation before opening Dash table
    confirm_and_open_dash_table()
    
    # Call the function to perform the processing
    # update_record(gdb_path, data)
        
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, 'Tool has completed')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    