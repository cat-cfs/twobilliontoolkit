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
            EstablishConnectionTool
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
