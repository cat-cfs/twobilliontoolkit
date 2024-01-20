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
import pandas as pd
from PyQt5.QtWidgets import QApplication, QTableWidget, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.SpatialTransformer.DataTrackerModule import DataTracker

#========================================================
# Classes
#========================================================
class DataTableApp(QWidget):
    def __init__(self, data):
        super().__init__()

        self.original_data = self.format_data(data)
        # save the original data to the current state
        self.data = self.original_data
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.populate_table()

        # Create a QHBoxLayout for the buttons
        button_layout = QHBoxLayout()

        self.edit_button = QPushButton('Save')
        self.edit_button.clicked.connect(self.save_data)

        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset_data)

        # Add buttons to the button layout
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.reset_button)

        # Add the table and button layout to the main layout
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_layout)
        
        self.setLayout(self.layout)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Data Table App')
        self.show()

    def item_changed(self, item):
        item.setForeground(QColor('red'))

    def format_data(self, data):
        df = pd.DataFrame.from_dict(data.data_dict, orient='index').reset_index()
        df.rename(columns={'index': 'project_spatial_id'}, inplace=True)
        return df

    def populate_table(self):
        self.table.setColumnCount(len(self.data.columns))
        self.table.setRowCount(len(self.data))
        
        # Set headers
        headers = [str(header) for header in self.data.columns]
        self.table.setHorizontalHeaderLabels(headers)

        for i in range(len(self.data.index)):
            for j in range(len(self.data.columns)):
                item = QTableWidgetItem(str(self.data.iloc[i, j]))

                # Check if the current column is in non_editable_columns
                if self.data.columns[j] in ['project_spatial_id', 'dropped']:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable | Qt.ItemIsSelectable)

                self.table.setItem(i, j, item)

        # Connect the itemChanged signal to a custom slot (function)
        self.table.itemChanged.connect(self.item_changed)

    def save_data(self):
        edited_rows = {}

        for i in range(len(self.data.index)):
            row_changes = {}

            for j in range(len(self.data.columns)):
                item = self.table.item(i, j)
                if item is not None:
                    edited_value = item.text()
                    original_value = str(self.original_data.iloc[i, j])

                    if edited_value != original_value:
                        row_changes[self.data.columns[j]] = edited_value

            if row_changes:
                # Assuming 'project_spatial_id' is the name of the column to use as the project_spatial_id
                project_spatial_id_value = self.data.at[i, 'project_spatial_id']
                edited_rows[project_spatial_id_value] = row_changes

        print("Rows with differences:")
        print(edited_rows)
        
        # Update the original data to the current state
        self.original_data = self.data
        self.reset_data()
        
    def reset_data(self):
        # Disconnect the itemChanged signal temporarily
        self.table.itemChanged.disconnect(self.item_changed)

        # Clear the table
        self.table.clear()
        
        self.data = self.original_data

        # Repopulate the table with the original data
        self.populate_table()

        # Reconnect the itemChanged signal
        self.table.itemChanged.connect(self.item_changed)

        # Print a message or perform any other necessary actions
        print("Data reset to original state")

#========================================================
# Functions
#========================================================

def create_duplicate():
    pass

def update_record(gdb, data, changes):
    pass



#========================================================
# Main
#========================================================
def main():
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
    # parser.add_argument('--changes', required=True, default=None, help='The changes that you want to update, in form "{project_spaital_id: {field: newvalue, field2:newvalue2...}, project_spatial_id: {field: newfield...}"')
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the values using the attribute notation
    # gdb_path = args.gdb
    data_tracker_path = args.data_tracker
    load_from = args.load
    save_to = args.save
    log_path = args.log
    # changes = args.changes
    
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
    
    data = DataTracker(data_tracker_path, load_from, save_to, log_path)
    
    app = QApplication([])
    window = DataTableApp(data)
    app.exec_()
    
    # # Ask for confirmation before opening Dash table
    # confirm_and_open_dash_table(data)
    
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
    