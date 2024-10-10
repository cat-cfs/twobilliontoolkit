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
    The script will be used to revise any records that have been created in the 2BT Spatial Tools. It provides a graphical user interface (GUI) for viewing and updating records in the Data Tracker. The GUI allows users to make changes to various fields, including 'project_spatial_id', 'project_number', 'in_raw_gdb', 'absolute_path', and 'entry_type'. Additionally, the script supports the creation of duplicate records when updating 'project_number', ensuring data integrity. Changes made through the GUI can be committed to either the Data Tracker Excel file or a Postgres DB table. The script also offers functionality to update associated Raw Data GDB layers and attachment folders.

Usage:
    python path/to/record_reviser.py --gdb /path/to/geodatabase --load [datatracker/database] --save [datatracker/database] --datatracker /path/to/datatracker.xlsx --changes "{key: {field: newvalue, field2: newvalue2...}, key2: {field: newfield}...}"
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
import datetime
import pandas as pd

from PyQt5.QtWidgets import QApplication, QTableWidget, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon

from twobilliontoolkit.Logger.Logger import Logger
from twobilliontoolkit.SpatialTransformer.Datatracker import Datatracker2BT


#========================================================
# Globals
#========================================================
session_added_entries = []

#========================================================
# Classes
#========================================================
class DataTableApp(QWidget):
    def __init__(self, data: Datatracker2BT, logger: Logger, gdb: str = None, filter: dict = None) -> None:
        """
        Initialize the DataTableApp with the provided data.

        Args:
            data (Datatracker2BT): An instance of the Datatracker2BT class. 
            logger (Logger): The Logger object to store and write to log files and the command line uniformly.
            gdb (str, optional): The path to the gdb that changes will be made to if applicable.
            filter (dict, optional): The dictionary of filters for the display data.
        """        
        super().__init__()
        
        self.logger = logger

        # Columns that are not editable and the key
        self.columns_noedit = ['project_spatial_id', 'created_at']
        self.columns_to_add = ['project_spatial_id', 'project_number', 'in_raw_gdb', 'absolute_file_path', 'entry_type']
        self.key = 'project_spatial_id'

        # Store the original and current dataframes
        self.filter = filter
        self.refresh_data(data)
        self.gdb = gdb
        
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
        
        # Enable sorting for the columns
        self.table.setSortingEnabled(True)

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
        self.setWindowTitle('Record Reviser')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'revision.png')
        self.setWindowIcon(QIcon(icon_path)) # Credit: https://www.flaticon.com/free-icons/revision
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()

    def refresh_data(self, data: Datatracker2BT) -> None:
        """
        Refresh the data in the application.

        Args:
            data (Datatracker2BT): The new data to be displayed.
        """
        # Update the data, original and current dataframe
        self.data = data
        formatted_data = self.format_data(data)
        self.original_dataframe = formatted_data[formatted_data['dropped'] != True]
  
        conditions = []
        # combined_condition = 

        # Filter out the data if there was a filter given
        if self.filter is not None:
            for key, value in self.filter.items():
                if key == "created_at":
                    if 'created_at' not in self.original_dataframe:
                        self.original_dataframe['created_at'] = pd.Series([pd.NaT] * len(self.original_dataframe), dtype='datetime64[ns]')
                    date = value.date()
                    condition = (
                        (self.original_dataframe.created_at.dt.date == date) | 
                        (pd.isna(self.original_dataframe.created_at))
                    )
                else:
                    condition = (self.original_dataframe[key] == value)
                
                conditions.append(condition)

            # Combine all conditions using & (and) operator
            combined_condition = conditions[0]
            for condition in conditions[1:]:
                combined_condition &= condition

        # Always add the condition for project_spatial_id
        combined_condition |= self.original_dataframe.project_spatial_id.isin(session_added_entries)

        # Apply the combined condition to the DataFrame
        self.original_dataframe = self.original_dataframe[combined_condition]
        
        # Make a working copy of the original dataframe
        self.dataframe = self.original_dataframe.copy()

    def format_data(self, data: Datatracker2BT) -> pd.DataFrame:
        
        """
        Format the raw data into a pandas DataFrame.

        Args:
            data (Datatracker2BT): Raw data to be formatted.

        Returns:
            pd.DataFrame: A formatted pandas DataFrame.
        """
        # Convert raw data to a DataFrame and rename index column
        dataframe = pd.DataFrame.from_dict(data.data_dict, orient='index').reset_index()
        dataframe.rename(columns={'index': self.key}, inplace=True)
        
        # Sort the DataFrame by the 'self.key' column alphabetically
        dataframe_sorted = dataframe.sort_values(by=self.key)

        return dataframe_sorted 

    def populate_table(self) -> None:
        """
        Populate the table with data from the dataframe.
        """
        # Filter the dataframe to include only the columns_to_add
        dataframe_filtered = self.dataframe[self.columns_to_add]
        
        # Set the number of columns and rows in the table
        self.table.setColumnCount(len(dataframe_filtered.columns))
        self.table.setRowCount(len(dataframe_filtered))
        
        # Set headers in the table
        headers = [str(header) for header in dataframe_filtered.columns]
        self.table.setHorizontalHeaderLabels(headers)

        # Populate each cell in the table with corresponding data
        for i in range(len(dataframe_filtered.index)):
            for j in range(len(dataframe_filtered.columns)):
                item = QTableWidgetItem(str(dataframe_filtered.iloc[i, j]))

                # Set flags for non-editable columns
                if dataframe_filtered.columns[j] in self.columns_noedit:
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
        # Get the project_spatial_id of the row changed
        row = item.row()
        project_spatial_id = self.table.item(row, 0).text()

        # Get the column name from the horizontal header
        column_name = self.table.horizontalHeaderItem(item.column()).text()

        # Fetch the original value using project_spatial_id
        original_value = str(self.original_dataframe.loc[self.original_dataframe[self.key] == project_spatial_id, column_name].values[0])

        # Highlight the cell if the value is different
        if item.text() != original_value:
            item.setForeground(QColor('red'))
        else:
            item.setForeground(QColor('black'))

    def save_changes(self) -> None:
        """
        Save the changes made in the GUI.
        """
        # Dictionary to store changes made in the GUI
        changes_dict = {}

        # Iterate over rows to identify changes
        for row in range(len(self.dataframe.index)):
            project_spatial_id = self.table.item(row, 0).text()
            row_changes = {}

            for column in range(len(self.dataframe.columns)):
                item = self.table.item(row, column)
                if item is not None:
                    edited_value = item.text()
                    column_name = self.table.horizontalHeaderItem(column).text()
                    original_value = str(self.original_dataframe.loc[self.original_dataframe[self.key] == project_spatial_id, column_name].values[0])

                    # Record changes if the value is different
                    if edited_value != original_value:
                        row_changes[column_name] = edited_value

            if row_changes:
                changes_dict[project_spatial_id] = row_changes

        # Log the changes
        self.logger.log(message=f'The changes made in the GUI were: {changes_dict}', tag='INFO')

        # Update the original data with the changes
        for project_spatial_id, changes in changes_dict.items():
            for column, value in changes.items():
                # Explicitly convert 'value' to the appropriate data type
                if self.original_dataframe[column].dtype == bool:
                    if value in ['True', 'False']:
                        value = bool(value)
                    else:
                        self.logger.log(message=f'The value {value} must be a bool in {column}', tag='ERROR')
                        return
                elif self.original_dataframe[column].dtype == int:
                    value = int(value)
                elif self.original_dataframe[column].dtype == float:
                    value = float(value)

                self.original_dataframe.loc[self.original_dataframe[self.key] == project_spatial_id, column] = value

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

        # Reset table sort so no confusion between dataframe and table occurs
        self.table.sortByColumn(0, Qt.AscendingOrder)
         
        # Repopulate the table with the original data
        self.populate_table()

        # Reconnect the itemChanged signal
        self.table.itemChanged.connect(self.item_changed)

        # Print a message or perform any other necessary actions
        self.logger.log(message=f'GUI data has been reset to original state', tag='INFO')

#========================================================
# Functions
#========================================================
def create_duplicate(data: Datatracker2BT, project_spatial_id: str, new_project_number: str) -> str:
    """
    Create a duplicate entry in the data for a given project with a new project number.

    Args:
        data (Datatracker2BT): An instance of Datatracker2BT.
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
        raw_data_path=entry_to_duplicate.get('raw_data_path'),
        raw_gdb_path=entry_to_duplicate.get('raw_gdb_path'),
        absolute_file_path=entry_to_duplicate.get('absolute_file_path'),
        in_raw_gdb=entry_to_duplicate.get('in_raw_gdb'),
        contains_pdf=entry_to_duplicate.get('contains_pdf'),
        contains_image=entry_to_duplicate.get('contains_image'),
        extracted_attachments_path=entry_to_duplicate.get('extracted_attachments_path'),
        editor_tracking_enabled=entry_to_duplicate.get('editor_tracking_enabled'),
        processed=entry_to_duplicate.get('processed'),
        entry_type=entry_to_duplicate.get('entry_type'),
    )
    
    # Add new project spatial id's to be included in the table
    session_added_entries.append(new_project_spatial_id)
        
    # Set the 'dropped' attribute to True for the original project
    data.set_data(project_spatial_id, dropped=True)

    return new_project_spatial_id

def update_records(data: Datatracker2BT, changes_dict: dict, gdb: str = None) -> None:
    """
    Update records in the data based on the changes provided in the dictionary.

    Args:
        data (Datatracker2BT): An instance of Datatracker2BT.
        changes_dict (dict): A dictionary containing changes for each project.
        gdb (str, optional): The geodatabase path. If provided, updates are applied to the geodatabase.
    """
    for project_spatial_id, value in changes_dict.items():
        # Check if the current change updated the project number
        new_project_number = value.get('project_number')
        if new_project_number:
            # Check if the project number entered was valid
            data.database_connection.connect(data.database_parameters)
            found = data.database_connection.read(
                schema=data.database_connection.schema,
                table='project_number',
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
            absolute_file_path=value.get('absolute_file_path'),
            entry_type=value.get('entry_type')
        )

    # Save the updated data
    data.save_data(update=True)
    
def record_reviser(logger: Logger, data: Datatracker2BT = None, gdb: str = None, load_from: str = 'database', save_to: str = 'database', datatracker: str = None, filter: dict = None, changes: str = None) -> None:
    """
    Handles calling the record reviser parts so the tool can be used outside of command-line as well.

    Args:
        logger (Logger): The Logger object to store and write to log files and the command line uniformly.
        data (Datatracker2BT, optional): An instance of Datatracker2BT.
        gdb (str, optional): The geodatabase path. If provided, updates are applied to the geodatabase.
        load_from (str, optional): Specifies where to retrieve the data from if it is not passed in. Default is 'database'.
        save_to (str, optional): Specifies where to save the data to. Default is 'database'.
        datatracker (str, optional): Path to the datatracker if load_from or save_to is specified as 'datatracker'.
        filter (dict, optional): A dictionary containing filters for the data to be displayed.
        changes (str, optional): A string dictionary containing changes for each project. If provided, no GUI will appear and only process the changes in the dictionary, else a GUI will appear and the user can alter the data as they see fit.
    """
    try:
        if not data:
            # Datatracker validation if data is not passed in
            if (load_from == 'datatracker' or save_to == 'datatracker'):
                if not datatracker:
                    raise argparse.ArgumentTypeError("If --load or --save is 'datatracker', --datatracker_path must be specified.")
                if not isinstance(datatracker, str) or not datatracker.strip():
                    raise ValueError(f'datatracker_path: {datatracker} must be a non-empty string.')
                if not datatracker.endswith('.xlsx'):
                    raise ValueError(f'datatracker_path: {datatracker} must be of type .xlsx.')
                if not os.path.exists(datatracker):
                    raise ValueError(f'datatracker_path: {datatracker} path does not exist.')
            
                
            # Create an instance of the Datatracker2BT class
            data = Datatracker2BT(datatracker, logger, load_from, save_to)
        
        if changes:
            # Parse the changes argument and update records
            changes_dict = ast.literal_eval(changes)
            update_records(data=data, changes_dict=changes_dict, gdb=gdb)
        else:
            # If no changes dict is provided, open a PyQt application for data visualization
            app = QApplication([])
            window = DataTableApp(data=data, gdb=gdb, filter=filter, logger=logger)
            app.exec_()  
    except Exception as error:
        logger.log(message=f"An unnexpected error has occured when running record_reviser: {error}", tag='ERROR')
            
#========================================================
# Main
#========================================================
def main():
    """ The main function of the record_reviser.py script """    
    # Initialize the argument parse
    parser = argparse.ArgumentParser(description='')
    
    # Define command-line arguments
    parser.add_argument('--gdb', required=True, default='', help='The new location or where an exsiting Geodatabase is located')
    parser.add_argument('--load', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to load from (datatracker or database)')
    parser.add_argument('--save', choices=['datatracker', 'database'], required=True, default='database', help='Specify what to save to (datatracker or database)')
    parser.add_argument('--datatracker', required=False, default=None, help='The new location or where an exsiting data tracker is located')
    parser.add_argument('--changes', required=False, default=None, help='The changes that you want to update, in form "{project_spaital_id: {field: newvalue, field2:newvalue2...}, project_spatial_id: {field: newfield}..."')
    parser.add_argument('--log', required=True, help='The location of the output log file for the tool.')
    parser.add_argument('--ps_script', default='', help='The location of the script to run commands if used.')
    
    # Parse the command-line arguments
    args = parser.parse_args()
        
    # Initialize the Logger
    logger = Logger(log_file=args.log, script_path=args.ps_script, auto_commit=True, tool_name=os.path.abspath(__file__))
    
    # Get the start time of the script
    start_time = time.time()
    logger.log(message=f'Tool is starting... Time: {datetime.datetime.now().strftime("%H:%M:%S")}', tag='INFO')
    
    # Call the entry function
    record_reviser(logger=logger, gdb=args.gdb, load_from=args.load, save_to=args.save, datatracker=args.datatracker, changes=args.changes)
         
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
    