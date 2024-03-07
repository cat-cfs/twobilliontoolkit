# -*- coding: utf-8 -*-

import arcpy
import json

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "TwoBillionTrees ArcGIS Toolbox"
        self.alias = "TwoBillionTreesArcGISToolbox"

        # List of tool classes associated with this toolbox
        self.tools = [
            EstablishConnectionTool,
            ReadDataTool,
            UpdateDataTool
        ]

class EstablishConnectionTool(object):
    def __init__(self):
        """Define the tool EstablishConnectionTool."""
        self.label = "Establish Connection"
        self.description = "Connect to an enterprise database connection."
        self.canRunInBackground = False

    def getParameterInfo(self):
        connection_file_param = arcpy.Parameter(
            displayName="Enterprise Connection File",
            name="connection_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        connection_file_param.filter.list = ["SDE"]
        
        table_name_param = arcpy.Parameter(
            displayName="Table Name",
            name="table_name",
            datatype="DETable",
            parameterType="Required",
            direction="Input"
        )
        
        return [connection_file_param, table_name_param]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed."""
        if parameters[0].value:
            # Validate and update parameters based on the selected connection file
            connection_file = parameters[0].valueAsText
            arcpy.env.workspace = connection_file

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """Connect to the enterprise geodatabase and retrieve data from the specified table."""
        try:
            # Get parameters
            connection_file = parameters[0].valueAsText
            table_name = parameters[1].valueAsText

            # Connect to the enterprise geodatabase
            arcpy.env.workspace = connection_file

            # Ping the database to establish connection
            with arcpy.da.SearchCursor(table_name, "*") as cursor:
                pass
            
        except Exception as e:
            arcpy.AddError(f"Error: {str(e)}")

class ReadDataTool(object):
    def __init__(self):
        """Define the tool ReadDataTool."""
        self.label = "Retrieve Data"
        self.description = "Connect to an enterprise geodatabase and retrieve data from a table."
        self.canRunInBackground = False

    def getParameterInfo(self):
        connection_file_param = arcpy.Parameter(
            displayName="Enterprise Connection File",
            name="connection_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        connection_file_param.filter.list = ["SDE"]
        
        table_name_param = arcpy.Parameter(
            displayName="Table Name",
            name="table_name",
            datatype="DETable",
            parameterType="Required",
            direction="Input"
        )
        
        output_list = arcpy.Parameter(
            displayName="output",
            name="output",
            datatype="Variant",
            parameterType="Derived",
            direction="Output"
        )

        return [connection_file_param, table_name_param, output_list]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed."""
        if parameters[0].value:
            # Validate and update parameters based on the selected connection file
            connection_file = parameters[0].valueAsText
            arcpy.env.workspace = connection_file

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """
        Connect to the enterprise geodatabase and retrieve data from the specified table.

        Parameters:
        - parameters: List of input parameters.
        - messages: List to store messages or errors.

        Returns:
        - (str) JSON representation of the retrieved data from the table.
        """
        try:
            # Get parameters
            connection_file = parameters[0].valueAsText
            table_name = parameters[1].valueAsText

            # Connect to the enterprise geodatabase
            arcpy.env.workspace = connection_file
            
            # Retrieve data from the table using a SearchCursor
            ret_list = [row for row in arcpy.da.SearchCursor(table_name, "*")]

            # Convert the list of rows to a dictionary
            data_dict = {"data": ret_list}

            # Convert the dictionary to a JSON string
            json_data = json.dumps(data_dict)

            # Set the output parameter with the JSON data
            arcpy.SetParameter(2, json_data)

            # Return the JSON data
            return json_data
        
        except Exception as e:
            arcpy.AddError(f"Error: {str(e)}")
            
class UpdateDataTool(object):
    def __init__(self):
        """Define the tool UpdateDataTool."""
        self.label = "Update data"
        self.description = "Connect to an enterprise geodatabase and insert data in a table."
        self.canRunInBackground = False

    def getParameterInfo(self):
        connection_file_param = arcpy.Parameter(
            displayName="Enterprise Connection File",
            name="connection_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        connection_file_param.filter.list = ["SDE"]
        
        table_name_param = arcpy.Parameter(
            displayName="Table Name",
            name="table_name",
            datatype="DETable",
            parameterType="Required",
            direction="Input"
        )
        
        insert_data = arcpy.Parameter(
            displayName="Insert Data",
            name="insert",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )

        return [connection_file_param, table_name_param, insert_data]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed."""
        if parameters[0].value:
            # Validate and update parameters based on the selected connection file
            connection_file = parameters[0].valueAsText
            arcpy.env.workspace = connection_file

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """Connect to the enterprise geodatabase and retrieve data from the specified table."""
        try:
            # Get parameters
            connection_file = parameters[0].valueAsText
            table_name = parameters[1].valueAsText
            insert_data = parameters[2].valueAsText

            # Connect to the enterprise geodatabase
            arcpy.env.workspace = connection_file

            # Update/Insert data into the table
            with arcpy.da.InsertCursor(table_name, ["site_id", "has_geometry"]) as cursor:
                # Assuming data_to_insert is a comma-separated string, you may need to adapt this based on your data format
                # data_list = insert_data.split(',')
                # cursor.insertRow(data_list)
                cursor.insertRow([10613, 1])
            
        except Exception as e:
            arcpy.AddError(f"Error: {str(e)}")
