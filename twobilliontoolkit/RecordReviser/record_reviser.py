#!/usr/bin/env python3
#~-~ encoding: utf-8 ~-~
# twobilliontoolkit/RecordReviser/record_reviser.py
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
File: twobilliontoolkit/RecordReviser/record_reviser.py
Created By:       Anthony Rodway
Email:            anthony.rodway@nrcan-rncan.gc.ca
Creation Date:    Wed January 17 10:30:00 PST 2024
Organization:     Natural Resources of Canada
Team:             Carbon Accounting Team

Description: 
    The script will be used to revise any records that have been created in the 2BT Spatial Tools. It provides a graphical user interface (GUI) for viewing and updating records in the Data Tracker. The GUI allows users to make changes to various fields, including 'project_spatial_id', 'project_number', 'in_raw_gdb', 'contains_pdf', 'contains_image', and 'contains_attachment'. Additionally, the script supports the creation of duplicate records when updating 'project_number', ensuring data integrity. Changes made through the GUI can be committed to either the Data Tracker Excel file or a Postgres DB table. The script also offers functionality to update associated Raw Data GDB layers and attachment folders.

Usage:
    python path/to/record_reviser.py --gdb /path/to/geodatabase --load [datatracker/database] --save [datatracker/database] --data_tracker /path/to/data_tracker.xlsx --log /path/to/logfile.txt --changes "{project_spatial_id: {field: newvalue, field2: newvalue2...}, project_spatial_id: {field: newfield}...}"
"""

#========================================================
# Imports
#========================================================
import os
import sys
import ast
import time
import arcpy
import argparse
import pandas as pd

from PyQt5.QtWidgets import QApplication, QTableWidget, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon

from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.SpatialTransformer.Datatracker import Datatracker

#========================================================
# Classes
#========================================================
class DataTableApp(QWidget):
    def __init__(self, data: Datatracker, gdb: str = None) -> None:
        """
        Initialize the DataTableApp with the provided data.

        Args:
            data (Datatracker): An instance of the Datatracker class.
            gdb (str, optional): The path to the gdb that changes will be made to if applicable.
        """        
        super().__init__()

        # Store the original and current dataframes
        self.data = data
        self.original_dataframe = self.format_data(data)
        self.dataframe = self.original_dataframe.copy()
        self.gdb = gdb
        
        # Columns that are not editable
        self.columns_noedit = ['project_spatial_id', 'dropped', 'project_path', 'raw_data_path']

        # Initialize the user interface
        self.init_ui()
        
    def init_ui(self) -> None:
        """
        Initialize the user interface components.
        """
         # Create the main layout
        self.layout = QVBoxLayout()

        # Create the table and populate it
        self.table = QTableWidget()
        self.populate_table()

        # Create a QHBoxLayout for buttons
        button_layout = QHBoxLayout()

        # Create Save and Reset buttons
        self.edit_button = QPushButton('Save')
        self.edit_button.clicked.connect(self.save_changes)

        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset_changes)

        # Add buttons to the button layout
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.reset_button)

        # Add the table and button layout to the main layout
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_layout)

        # Set the main layout for the widget
        self.setLayout(self.layout)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Recrord Reviser')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'revision.png')
        self.setWindowIcon(QIcon(icon_path)) # Credit: https://www.flaticon.com/free-icons/revision
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()

    def refresh_data(self, data: Datatracker) -> None:
        """
        Refresh the data in the application.

        Args:
            data (Datatracker): The new data to be displayed.
        """
        # Update the data, original and current dataframe
        self.data = data
        self.original_dataframe = self.format_data(data)
        self.dataframe = self.original_dataframe.copy()

    def format_data(self, data: Datatracker) -> pd.DataFrame:
        """
        Format the raw data into a pandas DataFrame.

        Args:
            data (Datatracker): Raw data to be formatted.

        Returns:
            pd.DataFrame: A formatted pandas DataFrame.
        """
        # Convert raw data to a DataFrame and rename index column
        dataframe = pd.DataFrame.from_dict(data.data_dict, orient='index').reset_index()
        dataframe.rename(columns={'index': 'project_spatial_id'}, inplace=True)
        return dataframe 

    def populate_table(self) -> None:
        """
        Populate the table with data from the dataframe.
        """
        # Set the number of columns and rows in the table
        self.table.setColumnCount(len(self.dataframe.columns))
        self.table.setRowCount(len(self.dataframe))
        
        # Set headers in the table
        headers = [str(header) for header in self.dataframe.columns]
        self.table.setHorizontalHeaderLabels(headers)

        # Populate each cell in the table with corresponding data
        for i in range(len(self.dataframe.index)):
            for j in range(len(self.dataframe.columns)):
                item = QTableWidgetItem(str(self.dataframe.iloc[i, j]))

                # Set flags for non-editable columns
                if self.dataframe.columns[j] in self.columns_noedit:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable | Qt.ItemIsSelectable)

                self.table.setItem(i, j, item) 
                
        # Resize columns to fit the content
        self.table.resizeColumnsToContents()   

        # Connect the itemChanged signal to a custom slot (function)
        self.table.itemChanged.connect(self.item_changed)

    def item_changed(self, item: QTableWidgetItem) -> None:
        """
        Handle changes in the table items.

        Args:
            item (QTableWidgetItem): The changed item in the table.
        """
        # Check if the changed value is different from the original value
        row = item.row()
        col = item.column()
        edited_value = item.text()
        original_value = str(self.original_dataframe.iloc[row, col])

        # Highlight the cell if the value is different
        if edited_value != original_value:
            item.setForeground(QColor('red'))
        else:
            item.setForeground(QColor('black'))

    def save_changes(self) -> None:
        """
        Save the changes made in the GUI.
        """
        # Dictionary to store changes made in the GUI
        changes_dict = {}

        # Iterate over rows and columns to identify changes
        for i in range(len(self.dataframe.index)):
            row_changes = {}

            for j in range(len(self.dataframe.columns)):
                item = self.table.item(i, j)
                if item is not None:
                    edited_value = item.text()
                    original_value = str(self.original_dataframe.iloc[i, j])

                    # Record changes if the value is different
                    if edited_value != original_value:
                        row_changes[self.dataframe.columns[j]] = edited_value

            if row_changes:
                # Store changes with project_spatial_id as key
                project_spatial_id_value = self.dataframe.at[i, 'project_spatial_id']
                changes_dict[project_spatial_id_value] = row_changes

        # Log the changes
        log(None, Colors.INFO, f'The changes made in the GUI were: {changes_dict}')

        # Update the original data with the changes
        for project_spatial_id, changes in changes_dict.items():
            row_index = self.dataframe[self.dataframe['project_spatial_id'] == project_spatial_id].index[0]
            for column, value in changes.items():
                # Explicitly convert 'value' to the appropriate data type
                if self.original_dataframe[column].dtype == bool:
                    value = bool(value)
                elif self.original_dataframe[column].dtype == int:
                    value = int(value)
                elif self.original_dataframe[column].dtype == float:
                    value = float(value)

                self.original_dataframe.at[row_index, column] = value

        # Update the records in the original data class
        update_records(self.data, changes_dict, self.gdb)
        
        # Refresh the data being put into the table and reset the table to the current state
        self.refresh_data(self.data)
        self.reset_changes()
        
    def reset_changes(self) -> None:
        """
        Reset the data in the table to its original state.
        """
        # Disconnect the itemChanged signal temporarily
        self.table.itemChanged.disconnect(self.item_changed)

        # Clear the table
        self.table.clear()
        
        # Reset the dataframe to the original state
        self.dataframe = self.original_dataframe.copy()

        # Repopulate the table with the original data
        self.populate_table()

        # Reconnect the itemChanged signal
        self.table.itemChanged.connect(self.item_changed)

        # Print a message or perform any other necessary actions
        log(None, Colors.INFO, f'GUI data has been reset to original state')

#========================================================
# Functions
#========================================================
def create_duplicate(data: Datatracker, project_spatial_id: str, new_project_number: str) -> str:
    """
    Create a duplicate entry in the data for a given project with a new project number.

    Args:
        data (Datatracker): An instance of Datatracker.
        project_spatial_id (str): The unique identifier of the project to duplicate.
        new_project_number (str): The new project number for the duplicated entry.

    Returns:
        str: The spatial identifier of the newly created duplicate entry.
    """
    # Retrieve data for the project to duplicate
    entry_to_duplicate = data.get_data(project_spatial_id)

    # Create a new spatial identifier for the duplicated project
    new_project_spatial_id = data.create_project_spatial_id(new_project_number)

    # Add the duplicated entry with the new project number to the data
    data.add_data(
        project_spatial_id=new_project_spatial_id,
        project_number=new_project_number,
        dropped=entry_to_duplicate.get('dropped'),
        project_path=entry_to_duplicate.get('project_path'),
        raw_data_path=entry_to_duplicate.get('raw_data_path'),
        absolute_file_path=entry_to_duplicate.get('absolute_file_path'),
        in_raw_gdb=entry_to_duplicate.get('in_raw_gdb'),
        contains_pdf=entry_to_duplicate.get('contains_pdf'),
        contains_image=entry_to_duplicate.get('contains_image'),
        extracted_attachments_path=entry_to_duplicate.get('extracted_attachments_path'),
        editor_tracking_enabled=entry_to_duplicate.get('editor_tracking_enabled'),
        processed=entry_to_duplicate.get('processed')
    )

    # Set the 'dropped' attribute to True for the original project
    data.set_data(project_spatial_id, dropped=True)

    return new_project_spatial_id

def update_records(data: Datatracker, changes_dict: dict, gdb: str = None) -> None:
    """
    Update records in the data based on the changes provided in the dictionary.

    Args:
        data (Datatracker): An instance of Datatracker.
        changes_dict (dict): A dictionary containing changes for each project.
        gdb (str, optional): The geodatabase path. If provided, updates are applied to the geodatabase.
    """
    for project_spatial_id, value in changes_dict.items():
        # Check if the current change updated the project number
        new_project_number = value.get('project_number')
        if new_project_number:
            # Check if the project number entered was valid
            data.database_connection.connect(data.database_connection.get_params())
            found = data.database_connection.read(
                table='bt_spatial_test.project_number',
                condition=f"project_number='{new_project_number}'"
            )               
            data.database_connection.disconnect()
            if not found:
                print(f'Project number {new_project_number} is not a valid project number in the database. Skipping changing this...')
                continue
            
            # Duplicate the project with the new project number
            old_project_spatial_id = 'proj_' + project_spatial_id
            project_spatial_id = create_duplicate(data, project_spatial_id, new_project_number)

            if gdb and data.get_data(project_spatial_id).get('in_raw_gdb') == True:
                # If geodatabase is provided, rename the corresponding entries
                arcpy.management.Rename(
                    os.path.join(gdb, old_project_spatial_id),
                    'proj_' + project_spatial_id
                )

                # Rename attachments path if it exists
                attachments_path = str(data.get_data(project_spatial_id).get('extracted_attachments_path'))
                if attachments_path not in ['nan', None, 'None']:
                    # update the attachment path
                    new_attachments_path = attachments_path.split('proj_')[0] + 'proj_' + project_spatial_id
                    
                    # Rename the path to the attachments
                    os.rename(
                        attachments_path, 
                        new_attachments_path
                    )
                    
                    # Set the corresponding attachments path
                    data.set_data(
                        project_spatial_id, extracted_attachments_path=new_attachments_path
                    )
                    
                    # Also need to update the linked geodatabase things
                    arcpy.management.Rename(
                        os.path.join(gdb, old_project_spatial_id) + '__ATTACH',
                        'proj_' + project_spatial_id + '__ATTACH'
                    )
                    arcpy.management.Rename(
                        os.path.join(gdb, old_project_spatial_id) + '__ATTACHREL',
                        'proj_' + project_spatial_id + '__ATTACHREL'
                    )

        # Update other attributes in the data
        data.set_data(
            project_spatial_id,
            in_raw_gdb=value.get('in_raw_gdb'),
            contains_pdf=value.get('contains_pdf'),
            contains_image=value.get('contains_image')
        )

    # Save the updated data
    data.save_changes(update=True)

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
    parser.add_argument('--gdb', required=True, default='', help='The new location or where an exsiting Geodatabase is located')
    parser.add_argument('--load', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to load from (datatracker or database)')
    parser.add_argument('--save', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to save to (datatracker or database)')
    parser.add_argument('--data_tracker', required=False, default=None, help='The new location or where an exsiting data tracker is located')
    parser.add_argument('--log', default=None, help='The new location or where an existing log file is located (optional)')
    parser.add_argument('--changes', required=False, default=None, help='The changes that you want to update, in form "{project_spaital_id: {field: newvalue, field2:newvalue2...}, project_spatial_id: {field: newfield}..."')
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the values using the attribute notation
    load_from = args.load
    save_to = args.save
    data_tracker_path = args.data_tracker
    
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
    
    gdb_path = args.gdb
    log_path = args.log
    
    # Create an instance of the Datatracker class
    data = Datatracker(data_tracker_path, load_from, save_to, log_path)
    
    if args.changes:
        try:
            # Parse the changes argument and update records
            changes_dict = ast.literal_eval(args.changes)
            update_records(data, changes_dict)
        except (ValueError, SyntaxError) as e:
            log(None, Colors.INFO, f'Error parsing changes argument: {e}')
    else:
        # If no changes are provided, open a PyQt application for data visualization
        changes_dict = None
        try:
            app = QApplication([])
            window = DataTableApp(data, gdb_path)
            app.exec_()  
        except RuntimeWarning as error:
            log(None, Colors.INFO, error)
         
    # Get the end time of the script and calculate the elapsed time
    end_time = time.time()
    log(None, Colors.INFO, 'Tool has completed')
    log(None, Colors.INFO, f'Elapsed time: {end_time - start_time:.2f} seconds')

#========================================================
# Main Guard
#========================================================
if __name__ == "__main__":
    sys.exit(main())
    