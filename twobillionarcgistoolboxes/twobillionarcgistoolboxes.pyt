# -*- coding: utf-8 -*-

import arcpy
import json
import time

class Toolbox(object):
    def __init__(self):
        """Define the toolbox twobillionarcgistoolboxes."""
        self.label = "TwoBillionTrees ArcGIS Toolbox"
        self.alias = "TwoBillionTreesArcGISToolbox"

        # List of tool classes associated with this toolbox
        self.tools = [
            EstablishConnectionTool,
            ReadDataTool,
            InsertDataTool,
            UpdateDataTool,
            CompleteProjectTool
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
        start = time.perf_counter()
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
        
        arcpy.AddMessage(f"This tool took {start - time.perf_counter():0.4f} seconds")

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
        start = time.perf_counter()
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
            
        arcpy.AddMessage(f"This tool took {start - time.perf_counter():0.4f} seconds")
            
class InsertDataTool(object):
    def __init__(self):
        """Define the InsertDataTool class."""
        # Tool information
        self.label = "Insert data"
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

        # Parameter 3: Site ID
        site_id_param = arcpy.Parameter(
            displayName="Site ID",
            name="site_id",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )
        
        # Parameter 4: Feature Layer
        feature_layer_param = arcpy.Parameter(
            displayName="Feature Layer",
            name="feature_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )

        return [connection_file_param, table_name_param, site_id_param, feature_layer_param]

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
        start = time.perf_counter()
        try:
            # Get parameters
            connection_file = parameters[0].valueAsText
            table_name = parameters[1].valueAsText
            site_id = parameters[2].valueAsText
            feature_layer = parameters[3].value
            
            # 
            with arcpy.da.SearchCursor(feature_layer, 'SHAPE@') as cursor:
                
                # Connect to the enterprise geodatabase
                arcpy.env.workspace = connection_file
                egdb_conn = arcpy.ArcSDESQLExecute(connection_file)
                
                # Loop through the selected features in the layer
                for row in cursor:                  
                    # Project the polygon to Canadian Albers (wkid 102001)
                    target_Ref = arcpy.SpatialReference(102001)
                    polygon_projected = row[0].projectAs(target_Ref)   
                    
                    # Get all parts of the project polygon and construct a new polygon with no z or m-coordinates
                    array_of_polygons = arcpy.Array(polygon_projected.getPart())
                    projected_multipolygon = arcpy.Polygon(array_of_polygons, target_Ref)
                    
                    # Construct the SQL query for insertion
                    sql_insert = f'INSERT INTO {table_name} ("site_id", "geom") VALUES ({site_id}, ST_GeomFromText(\'{projected_multipolygon.WKT}\', 102001))'
                    egdb_conn.execute(sql_insert)
                  
            # Get the feature layer location  
            description = arcpy.Describe(feature_layer)
                    
            # Start an edit session
            edit = arcpy.da.Editor(description.path) 
            edit.startEditing(False, True) 
            edit.startOperation()
            
            with arcpy.da.UpdateCursor(feature_layer, 'bt_site_id') as cursor:                
                # Loop through the selected features in the layer
                for row in cursor:                                        
                    row[0] = site_id
                    cursor.updateRow(row)
                
            # Stop the edit operation and session
            edit.stopOperation()
            edit.stopEditing(True)

        except Exception as e:
            # Handle and log errors
            arcpy.AddError(f"Error: {str(e)}")

        arcpy.AddMessage(f"This tool took {start - time.perf_counter():0.4f} seconds")

class UpdateDataTool(object):
    def __init__(self):
        """Define the UpdateDataTool class."""
        # Tool information
        self.label = "Update data"
        self.description = "Connect to an enterprise geodatabase and update data in a table."
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

        # Parameter 3: Site ID
        site_id_param = arcpy.Parameter(
            displayName="Site ID",
            name="site_id",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )

        # Parameter 4: Feature Layer
        feature_layer_param = arcpy.Parameter(
            displayName="Feature Layer",
            name="feature_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )

        return [connection_file_param, table_name_param, site_id_param, feature_layer_param]

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
        Connect to the enterprise geodatabase and update data in the specified table.

        Parameters:
        - parameters: List of input parameters.
        - messages: List to store messages or errors.
        """
        start = time.perf_counter()
        try:
            # Get parameters
            connection_file = parameters[0].valueAsText
            table_name = parameters[1].valueAsText
            site_id = parameters[2].valueAsText
            feature_layer = parameters[3].value

            with arcpy.da.SearchCursor(feature_layer, 'SHAPE@') as cursor:
                
                # Connect to the enterprise geodatabase
                arcpy.env.workspace = connection_file
                egdb_conn = arcpy.ArcSDESQLExecute(connection_file)
                
                # Construct the SQL query for updating the entries 
                sql_update = f'UPDATE {table_name} SET "dropped" = true WHERE "site_id" = {site_id}' 
                egdb_conn.execute(sql_update)
                
                # Loop through the selected features in the layer
                for row in cursor:                    
                    # Project the polygon to Canadian Albers (wkid 102001)
                    target_Ref = arcpy.SpatialReference(102001)
                    polygon_projected = row[0].projectAs(target_Ref)   
                    
                    # Get all parts of the project polygon and construct a new polygon with no z or m-coordinates
                    array_of_polygons = arcpy.Array(polygon_projected.getPart())
                    projected_multipolygon = arcpy.Polygon(array_of_polygons, target_Ref)
                    
                    # Construct the SQL query for insertion
                    sql_insert = f'INSERT INTO {table_name} ("site_id", "geom") VALUES ({site_id}, ST_GeomFromText(\'{projected_multipolygon.WKT}\', 102001))'
                    egdb_conn.execute(sql_insert)
               
            # Get the feature layer location  
            description = arcpy.Describe(feature_layer)
                    
            # Start an edit session
            edit = arcpy.da.Editor(description.path) 
            edit.startEditing(False, True) 
            edit.startOperation()
                 
            with arcpy.da.UpdateCursor(feature_layer, 'bt_site_id') as cursor:                
                # Loop through the selected features in the layer
                for row in cursor:                                        
                    row[0] = site_id
                    cursor.updateRow(row)
                    
            # Stop the edit operation and session
            edit.stopOperation()
            edit.stopEditing(True)
                            
        except Exception as e:
            # Handle and log errors
            arcpy.AddError(f"Error: {str(e)}")
            
        arcpy.AddMessage(f"This tool took {start - time.perf_counter():0.4f} seconds")

class CompleteProjectTool(object):
    def __init__(self):
        """Define the CompleteProjectTool class."""
        # Tool information
        self.label = "Complete Project"
        self.description = "Flag the project entry in the database as completed (looked at and processed) by the analyst and the project is all done in this step."
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

        # Parameter 3: Project Spatial id
        project_id_param = arcpy.Parameter(
            displayName="Project Spatial id",
            name="project_id",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        return [connection_file_param, table_name_param, project_id_param]

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
        Connect to the enterprise geodatabase and update data in the specified table.

        Parameters:
        - parameters: List of input parameters.
        - messages: List to store messages or errors.
        """
        start = time.perf_counter()
        try:
            # Get parameters
            connection_file = parameters[0].valueAsText
            table_name = parameters[1].valueAsText
            project_id = parameters[2].valueAsText
            project_id = project_id.replace('proj_', '')
            
            # Connect to the enterprise geodatabase
            arcpy.env.workspace = connection_file
            egdb_conn = arcpy.ArcSDESQLExecute(connection_file)
            
            # Construct the SQL query for updating the entry
            sql_update = f'UPDATE {table_name} SET "analyst_processed" = true WHERE "project_spatial_id" = \'{project_id}\'' 
            egdb_conn.execute(sql_update)
             
        except Exception as e:
            # Handle and log errors
            arcpy.AddError(f"Error: {str(e)}")
            
        arcpy.AddMessage(f"This tool took {start - time.perf_counter():0.4f} seconds")
        