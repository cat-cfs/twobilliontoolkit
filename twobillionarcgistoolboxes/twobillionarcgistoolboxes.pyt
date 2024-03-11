# -*- coding: utf-8 -*-

import arcpy
import json

class Toolbox(object):
    def __init__(self):
        """Define the toolbox twobillionarcgistoolboxes."""
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
        """Define the EstablishConnectionTool class."""
        # Tool information
        self.label = "Establish Connection"
        self.description = "Connect to an enterprise database connection."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define input parameters for the tool."""
        # Parameter 1: Enterprise Connection File
        connection_file_param = arcpy.Parameter(
            displayName="Enterprise Connection File",
            name="connection_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        connection_file_param.filter.list = ["SDE"]

        # Parameter 2: Table Name
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
        """Update parameters based on the selected connection file."""
        if parameters[0].value:
            connection_file = parameters[0].valueAsText
            arcpy.env.workspace = connection_file

        return

    def updateMessages(self, parameters):
        """Modify messages created by internal validation."""
        return

    def execute(self, parameters, messages):
        """
        Connect to the enterprise geodatabase and establish a connection.

        Parameters:
        - parameters: List of input parameters.
        - messages: List to store messages or errors.
        """
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
            # Handle and log errors
            arcpy.AddError(f"Error: {str(e)}")

class ReadDataTool(object):
    def __init__(self):
        """Define the ReadDataTool class."""
        # Tool information
        self.label = "Retrieve Data"
        self.description = "Connect to an enterprise geodatabase and retrieve data from a table."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define input parameters for the tool."""
        # Parameter 1: Enterprise Connection File
        connection_file_param = arcpy.Parameter(
            displayName="Enterprise Connection File",
            name="connection_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        connection_file_param.filter.list = ["SDE"]

        # Parameter 2: Table Name
        table_name_param = arcpy.Parameter(
            displayName="Table Name",
            name="table_name",
            datatype="DETable",
            parameterType="Required",
            direction="Input"
        )

        # Parameter 3: Output
        output_list = arcpy.Parameter(
            displayName="Output",
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
        """Update parameters based on the selected connection file."""
        if parameters[0].value:
            connection_file = parameters[0].valueAsText
            arcpy.env.workspace = connection_file

        return

    def updateMessages(self, parameters):
        """Modify messages created by internal validation."""
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
            # Handle and log errors
            arcpy.AddError(f"Error: {str(e)}")
            
class UpdateDataTool(object):
    def __init__(self):
        """Define the UpdateDataTool class."""
        # Tool information
        self.label = "Update data"
        self.description = "Connect to an enterprise geodatabase and insert data in a table."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define input parameters for the tool."""
        # Parameter 1: Enterprise Connection File
        connection_file_param = arcpy.Parameter(
            displayName="Enterprise Connection File",
            name="connection_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        connection_file_param.filter.list = ["SDE"]

        # Parameter 2: Table Name
        table_name_param = arcpy.Parameter(
            displayName="Table Name",
            name="table_name",
            datatype="DETable",
            parameterType="Required",
            direction="Input"
        )

        # Parameter 3: Insert Data
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
        """Update parameters based on the selected connection file."""
        if parameters[0].value:
            connection_file = parameters[0].valueAsText
            arcpy.env.workspace = connection_file

        return

    def updateMessages(self, parameters):
        """Modify messages created by internal validation."""
        return

    def execute(self, parameters, messages):
        """
        Connect to the enterprise geodatabase and insert data into the specified table.

        Parameters:
        - parameters: List of input parameters.
        - messages: List to store messages or errors.
        """
        try:
            # Get parameters
            connection_file = parameters[0].valueAsText
            table_name = parameters[1].valueAsText
            insert_data = parameters[2].valueAsText

            # Split insert_data into site_id and geometry
            data_list = insert_data.split(',', 1)

            # Connect to the enterprise geodatabase
            arcpy.env.workspace = connection_file

            # Convert the geometry string to a polygon
            polygon = arcpy.AsShape(data_list[1], True)
            polygon = arcpy.Polygon(polygon.getPart(0))
            
            # Display the WKT representation of the geometry
            # arcpy.AddMessage(polygon.WKT)

            # Construct the SQL query for insertion
            sql = f'INSERT INTO {table_name} ("site_id", "geom") VALUES ({data_list[0]}, ST_GeomFromText(\'{polygon.WKT}\', 102001))'

            # Execute the SQL query
            egdb_conn = arcpy.ArcSDESQLExecute(connection_file)
            egdb_conn.execute(sql)

        except Exception as e:
            # Handle and log errors
            arcpy.AddError(f"Error: {str(e)}")
