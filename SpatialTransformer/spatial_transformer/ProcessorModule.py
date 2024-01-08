# spatial_transformer/ProcessorModule.py
#========================================================
# Imports
#========================================================
from common import *
from DataTrackerModule import DataTracker

import re
import tempfile
import xml.etree.ElementTree as ET

#========================================================
# Helper Class
#========================================================
class Processor:
    def __init__(self, params):
        '''
        Initializes the SpatialData class with input parameters.

        Parameters:
            params: Instance of the StartupParameters class.
        
        Returns:
            None
        '''
        self.params = params
        self._spatial_files = []
        self.temp_directory = tempfile.gettempdir() + '\spatial_trans'
      
    @property
    def spatial_files(self):
        '''
        Property getter for spatial files.

        Returns:
            list: List of spatial file paths.
        '''
        return self._spatial_files
        
    def search_for_spatial_data(self):
        '''
        Walk through the directory structure and extract any spatial or data sheet file paths.

        Populates the `spatial_files` and `data_sheets` lists with file paths.

        Files ending with SPATIAL_FILE_EXTENSIONS are added to `spatial_files`, and
        files ending with DATA_SHEET_EXTENSIONS are added to `data_sheets`.
        
        Returns: 
            None
        '''
        # Step through unzip output path and keep track of paths
        for root, dirs, files in os.walk(self.params.output):
            for dir in dirs:
                if dir.endswith('.gdb'):
                    self.spatial_files.append(os.path.join(root, dir))
                    dirs.remove(dir)  # Exclude .gdb directory from further recursion
            for file in files:
                file = file.lower()
                if file.endswith(SPATIAL_FILE_EXTENSIONS) or file.endswith(DATA_SHEET_EXTENSIONS) or file.endswith(LAYOUT_FILE_EXTENSIONS) or file.endswith(IMAGE_FILE_EXTENSIONS):
                    self.spatial_files.append(os.path.join(root, file))                   
      
    def process_spatial_files(self):
        '''
        Process all of the found spatial files.

        Parameters:
            master_df: Master data sheet as a pandas DataFrame.
        
        Returns:
            None
        '''
        # Create the Data class to hold any data tracker information
        data = DataTracker(self.params.datatracker, self.params.load_from, self.params.save_to)
        master_df = self.params.masterdata

        for file in self.spatial_files:
            # Check project numbers and format the result
            formatted_result = self._check_project_numbers(file, master_df)
            formatted_result = formatted_result.upper()

            # Create a unique identifier for the project spatial ID
            formatted_project_spatial_id = data._create_project_spatial_id(formatted_result)

            # Print file information if debugging is enabled
            if self.params.debug:
                print(file)
                print(formatted_project_spatial_id)

            # Convert the raw data path to a relative path and extract the project path
            raw_data_path = os.path.relpath(file, self.params.output)
            project_path = raw_data_path.split("\\")[0]

            # Call a method to process raw data matching
            self._call_raw_data_match(formatted_project_spatial_id, raw_data_path, data)

            # Add data to the data class     
            data.add_data(
                project_spatial_id=formatted_project_spatial_id, 
                project_number=formatted_result, 
                project_path=project_path, 
                raw_data_path=raw_data_path, 
                in_raw_gdb=False, 
                contains_pdf=False, 
                contains_image=False
            )
            
            try: 
                # Check the file type and call the appropriate processing method
                lowercase_file = file.lower()
                if lowercase_file.endswith(LAYOUT_FILE_EXTENSIONS):
                    logging(self.params.log, Colors.WARNING, f'Layout file: {file} will be added to data tracker but not resulting gdb.\n')
                elif lowercase_file.endswith(DATA_SHEET_EXTENSIONS):
                    logging(self.params.log, Colors.WARNING, f'Datasheet: {file} will be added to data tracker but not resulting gdb.\n')
                elif lowercase_file.endswith(IMAGE_FILE_EXTENSIONS):
                    logging(self.params.log, Colors.WARNING, f'Image/PDF file: {file} will be added to data tracker but not resulting gdb.\n')
                    
                    # Update data tracker based on specific file types
                    if lowercase_file.endswith('.pdf'):
                        data.set_data(project_spatial_id=formatted_project_spatial_id, contains_pdf=True)
                    else:
                        data.set_data(project_spatial_id=formatted_project_spatial_id, contains_image=True)
                elif lowercase_file.endswith('.shp'):
                    self._process_shp(file, formatted_project_spatial_id, data)         
                elif lowercase_file.endswith(('.kml', '.kmz')):
                    self._process_kml_kmz(file, formatted_project_spatial_id, data)    
                elif lowercase_file.endswith('.geojson'):
                    self._process_json(file, formatted_project_spatial_id, data)
                elif lowercase_file.endswith('.gdb'):
                    self._process_gdb(file, formatted_project_spatial_id, data)
                elif lowercase_file.endswith(('.gpkg', '.sqlite')):
                    if self.params.debug:
                        print(f'Geopackage file: {file} will be added to data tracker but not resulting gdb.\n')
            except Exception as error:
                logging(self.params.log, Colors.ERROR, error)

        # Save the data tracker before returning
        data._save_data()
        logging(self.params.log, Colors.INFO, f'The data tracker "{self.params.datatracker}" has been created successfully.')
         
    def _check_project_numbers(self, file_path, master_df):
        '''
        Check project numbers against a master data sheet.

        Parameters:
            file_path: Filepath to check.
            master_df: Master data sheet as a pandas DataFrame.
        
        Returns:
            str: the formatted result for the project number of the spatial file path.
        '''
        # Define a regular expression pattern to extract project numbers and search for pattern in file path
        pattern = r'(\d{4})[\s_–-]*([a-zA-Z]{3})[\s_–-]*(\d{3})'
        search = re.search(pattern, file_path)
        
        # If no match is found, log a warning and assign an arbitrary project number
        if not search:
            logging(self.params.log, Colors.WARNING, f'Could not find a project number for: {file_path} - Giving it an arbitrary project number "0000 XXX - 000"')
            formatted_result = '0000 XXX - 000'
        else:
            # Format the result using the matched groups
            formatted_result = '{} {} - {}'.format(search.group(1), search.group(2), search.group(3))

        # Check if the project number is found in the master datasheet
        project_found = master_df['Project Number'].str.replace(' ', '').eq(formatted_result.replace(' ', '').upper()).any()
        if not project_found:
            logging(self.params.log, Colors.WARNING, f'The project number does not match any in the master datasheet')
            
        return formatted_result
        
    def _call_raw_data_match(self, current_spatial_id, raw_data_path, data):
        """
        Call the method that finds a matching raw data path and returns the project spatial id.

        Args:
            current_spatial_id (str): The current spatial project id being checked.
            raw_data_path (str): The raw data path to be search in the dictionary.
            data (dict): Data dictionary.

        Returns:
            None
        """
        # Find a corresponding project spatial ID in the data dictionary based on the raw data path
        found_match = data._find_matching_spatial_id(raw_data_path)
        if found_match is not None:
            logging(self.params.log, Colors.WARNING, f'Raw path: {raw_data_path} already exists in the data tracker! -  Current Spatial ID: {current_spatial_id} Matching Spatial ID: {found_match}')    

    def _process_shp(self, file, formatted_project_spatial_id, data):
        """
        Process shapefile.

        Args:
            file (str): Path to the shapefile.
            formatted_project_spatial_id (str): Formatted project spatial ID.
            data (dict): Data dictionary.

        Returns:
            None
        """
        # Export features from shapefile to a geodatabase
        arcpy.conversion.ExportFeatures(
            file,
            self.params.gdb + f'\proj_{formatted_project_spatial_id}'
        )
        
        # Change the flag to indicate it was succefully put into the Geodatabase
        data.set_data(project_spatial_id=formatted_project_spatial_id, in_raw_gdb=True)


    def remove_cascading_style(self, file):
        """
        Remove cascading styles from KML-XML.
        
        Parameters:
            file (str): Path to the KML file.
        
        Returns:
            str: Path to modified XML root.
        """
        # Register XML namespaces
        ET.register_namespace("", "http://www.opengis.net/kml/2.2")
        ET.register_namespace("gx", "http://www.google.com/kml/ext/2.2")
        ET.register_namespace("atom", "http://www.w3.org/2005/Atom")

        # Read KML content from file
        with open(file, 'r', encoding='utf-8') as file:
            kml_content = file.read()
        
        root = ET.fromstring(kml_content)
        cascading_styles = root.findall(".//{http://www.google.com/kml/ext/2.2}CascadingStyle")

        for cascading_style in cascading_styles:
            parent = root.find(".//{http://www.opengis.net/kml/2.2}Document")
            parent.remove(cascading_style)

        # Write modified KML content to a new file
        kml_output_no_gx_path = os.path.join(self.temp_directory, 'KMLWithoutGX.kml')
        ET.ElementTree(root).write(kml_output_no_gx_path, encoding="utf-8", xml_declaration=True)

        return kml_output_no_gx_path  
    
    def _process_kml_kmz(self, file, formatted_project_spatial_id, data): 
        """
        Process KML/KMZ files.

        Parameters:
            file (str): Path to the KML/KMZ file.
            formatted_project_spatial_id (str): Formatted project spatial ID.
            data (dict): Data dictionary.

        Returns:
            None
        """
        # Create temporary directory if it doesn't exist, otherwise, recreate it
        if not os.path.exists(self.temp_directory):
            os.makedirs(self.temp_directory)
        else:
            shutil.rmtree(self.temp_directory)
            os.makedirs(self.temp_directory)

        # Remove cascading styles from KML content
        if file.endswith('.kml'):
            file = self.remove_cascading_style(file)

        # Convert modified KML to layer and copy to geodatabase
        arcpy.conversion.KMLToLayer(file, self.temp_directory, "kml_layer", "NO_GROUNDOVERLAY")   
        
        # Make the workspace the output gdb in the temp folder
        arcpy.env.workspace = os.path.join(self.temp_directory, 'kml_layer.gdb/Placemarks')
        
        # Set starting raw data path and a flag for skipping first iteration
        base_raw_data_path = data.get_data(formatted_project_spatial_id)['raw_data_path']
        first_feature_class_processed = False
        
        # Iterate through the feature classes and rename them
        feature_classes = arcpy.ListFeatureClasses()
        for index, feature_class in enumerate(feature_classes):           
            if first_feature_class_processed:
                # Get data for the current feature and create a new project spatial ID
                current_feature_data = data.get_data(formatted_project_spatial_id)
                spatial_project_id = data._create_project_spatial_id(current_feature_data['project_number'])
                
                # Add data for the new project spatial ID
                data.add_data(
                    project_spatial_id=spatial_project_id,
                    project_number=current_feature_data['project_number'],
                    project_path=current_feature_data['project_path'],
                    raw_data_path=current_feature_data['raw_data_path'],
                    in_raw_gdb=False,
                    contains_pdf=False,
                    contains_image=False
                )
                
                # Update the formatted project spatial ID
                formatted_project_spatial_id = spatial_project_id
            
            # Create a new name and export feature class
            new_name = f"proj_{formatted_project_spatial_id}"
            arcpy.management.Copy(
                os.path.join(self.temp_directory, f'kml_layer.gdb/Placemarks/{feature_class}'),
                os.path.join(self.params.gdb, new_name)
            )   
            
            # Set the flag to indicate that the first feature class has been processed
            first_feature_class_processed = True
            
            new_raw_data_path = os.path.join(base_raw_data_path, feature_class)
            self._call_raw_data_match(formatted_project_spatial_id, new_raw_data_path, data)
            
            # Update the entry of the Geodatabase feature class
            data.set_data(
                project_spatial_id=formatted_project_spatial_id, 
                raw_data_path=new_raw_data_path, 
                in_raw_gdb=True
            )
        
    def _process_json(self, file, formatted_project_spatial_id, data):
        """
        Process GeoJSON files.

        Parameters:
            file (str): Path to the GeoJSON file.
            formatted_project_spatial_id (str): Formatted project spatial ID.
            data (dict): Data dictionary.

        Returns:
            None
        """
        # Export features from GeoJSON to a geodatabase
        arcpy.conversion.JSONToFeatures(
            file,
            self.params.gdb + f'\proj_{formatted_project_spatial_id}'
        )
        
        # Change the flag to indicate it was succefully put into the Geodatabase
        data.set_data(
            project_spatial_id=formatted_project_spatial_id, in_raw_gdb=True
        )
        
    def _process_gdb(self, file, formatted_project_spatial_id, data): 
        """
        Process GeoDatabase files.

        Parameters:
            file (str): Path to the GeoDatabase file.
            formatted_project_spatial_id (str): Formatted project spatial ID.
            data (dict): Data dictionary.

        Returns:
            None
        """
        # Set the workspace to the specified .gdb
        arcpy.env.workspace = file
        
        # Set starting raw data path and a flag for skipping first iteration
        base_raw_data_path = data.get_data(formatted_project_spatial_id)['raw_data_path']
        first_feature_class_processed = False
        
        # Iterate through the feature classes and tables
        feature_tables = arcpy.ListTables()
        feature_classes = arcpy.ListFeatureClasses()
        for feature in feature_classes + feature_tables:
            if first_feature_class_processed:
                # Get data for the current feature and create a new project spatial ID
                current_feature_data = data.get_data(formatted_project_spatial_id)
                spatial_project_id = data._create_project_spatial_id(current_feature_data['project_number'])
                
                # Add data for the new project spatial ID
                data.add_data(
                    project_spatial_id=spatial_project_id,
                    project_number=current_feature_data['project_number'],
                    project_path=current_feature_data['project_path'],
                    raw_data_path=current_feature_data['raw_data_path'],
                    in_raw_gdb=False,
                    contains_pdf=False,
                    contains_image=False
                )
                
                # Update the formatted project spatial ID
                formatted_project_spatial_id = spatial_project_id
            
            if arcpy.Describe(feature).dataType == 'FeatureClass':
                # Create a new name and export feature class
                new_name = f"proj_{formatted_project_spatial_id}"
                arcpy.conversion.ExportFeatures(
                    os.path.join(file, feature),
                    os.path.join(self.params.gdb, new_name)
                )
                
                # Update the entry of the Geodatabase feature class
                data.set_data(
                    project_spatial_id=formatted_project_spatial_id, 
                    in_raw_gdb=True
                )
            
            # Set the flag to indicate that the first feature class has been processed
            first_feature_class_processed = True
            
            new_raw_data_path = os.path.join(base_raw_data_path, feature)
            self._call_raw_data_match(formatted_project_spatial_id, new_raw_data_path, data)
            
            # Update the entry of the Geodatabase feature class
            data.set_data(
                project_spatial_id=formatted_project_spatial_id, 
                raw_data_path=new_raw_data_path, 
            )

    def __str__(self):
        '''
        Redefines the string representation of the class.

        Returns:
        - str: String representation of the SpatialData class.
        '''
        return f'\nSpatialData Class\nSpatial Files: {self.spatial_files}\nData Sheets: {self.data_sheets}'
    