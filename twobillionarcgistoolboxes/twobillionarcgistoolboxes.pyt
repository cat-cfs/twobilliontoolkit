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
            InsertDataTool
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

        # Parameter 4: New Geometry
        geometry_param = arcpy.Parameter(
            displayName="New Geometry",
            name="new_geometry",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )

        return [connection_file_param, table_name_param, site_id_param, geometry_param]

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
            site_id = parameters[2].valueAsText
            geometry = parameters[3].valueAsText

            # Connect to the enterprise geodatabase
            arcpy.env.workspace = connection_file

            # Convert the geometry string to a polygon
            polygon = arcpy.AsShape(geometry, True)
            
            # Project the polygon to Canadian Albers (wkid 102001)
            target_Ref = arcpy.SpatialReference(102001)
            polygon_projected = polygon.projectAs(target_Ref)   
            
            # Get all parts of the project polygon and construct a new polygon with no z or m-coordinates
            array_of_polygons = arcpy.Array(polygon_projected.getPart())
            projected_multipolygon = arcpy.Polygon(array_of_polygons, target_Ref)
            
            # Construct the SQL query for insertion
            sql = f'INSERT INTO {table_name} ("site_id", "geom") VALUES ({site_id}, ST_GeomFromText(\'{projected_multipolygon.WKT}\', 102001))'

            # Execute the SQL query
            egdb_conn = arcpy.ArcSDESQLExecute(connection_file)
            egdb_conn.execute(sql)

        except Exception as e:
            # Handle and log errors
            arcpy.AddError(f"Error: {str(e)}")

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

        # Parameter 4: New Geometry
        new_geometry_param = arcpy.Parameter(
            displayName="New Geometry",
            name="new_geometry",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )

        return [connection_file_param, table_name_param, site_id_param, new_geometry_param]

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
        try:
            # Get parameters
            connection_file = parameters[0].valueAsText
            table_name = parameters[1].valueAsText
            site_id = parameters[2].valueAsText
            new_geometry = parameters[3].valueAsText

            # Connect to the enterprise geodatabase
            arcpy.env.workspace = connection_file

            # Convert the new geometry string to a polygon
            new_polygon = arcpy.AsShape(new_geometry, True)

            # Project the new polygon to Canadian Albers (wkid 102001)
            target_ref = arcpy.SpatialReference(102001)
            new_polygon = new_polygon.projectAs(target_ref)

            # Remove the Z coordinates from the polygon
            new_polygon = arcpy.Polygon(new_polygon.getPart(0))

            # Construct the SQL query for updating the entry
            sql = f'UPDATE {table_name} SET "geom" = ST_GeomFromText(\'{new_polygon.WKT}\', 102001) WHERE "site_id" = \'{site_id}\''

            # Execute the SQL query
            egdb_conn = arcpy.ArcSDESQLExecute(connection_file)
            egdb_conn.execute(sql)

        except Exception as e:
            # Handle and log errors
            arcpy.AddError(f"Error: {str(e)}")
