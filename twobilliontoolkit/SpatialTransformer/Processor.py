# twobilliontoolkit/SpatialTransformer/Processor.py
#========================================================
# Imports
#========================================================
import arcpy
import re
import tempfile
import xml.etree.ElementTree as ET
import arcpy.management
import win32wnet
import arcgisscripting

from twobilliontoolkit.SpatialTransformer.common import *
from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.GeoAttachmentSeeker.geo_attachment_seeker import find_attachments
from twobilliontoolkit.SpatialTransformer.Datatracker import Datatracker2BT
from twobilliontoolkit.SpatialTransformer.Parameters import Parameters

#========================================================
# Helper Class
#========================================================
class Processor:
    def __init__(self, params: Parameters) -> None:
        """
        Initializes the Processor class with input parameters.

        Args:
            params (Parameters): Instance of the Parameters class.
        """
        self.params = params
        
        # Create the Data class to hold any data tracker information
        self.data = Datatracker2BT(params.datatracker, params.load_from, params.save_to)
        
        self.spatial_files = []
        self.temp_directory = tempfile.gettempdir() + '\spatial_trans'
       
    def create_datatracker_entries(self) -> None:
        """
        Creates data tracker entries by processing files and directories within the output path.

        This function walks through the specified output directory, processes different file types, and creates entries in the data tracker. It handles geodatabases, shapefiles, KML/KMZ files,
        GeoJSON files, GeoPackages, and other file types, ensuring that they are correctly added to the data tracker.

        Args:
            None

        Returns:
            None
        """  
        # Step through unzip output path
        for root, dirs, files in os.walk(self.params.output):
            for dir in dirs:
                # Built full directory path
                directory_path = f"{root}\{dir}"
                
                # Skip over the gdb if tool is running a second time if it is somehow in the folder
                if dir is self.params.gdb_path:
                    continue
                
                if dir.endswith('.gdb'):
                    # Set the workspace to the specified .gdb
                    arcpy.env.workspace = directory_path
                                        
                    # Iterate through the feature classes and tables
                    feature_tables = arcpy.ListTables()
                    feature_classes = arcpy.ListFeatureClasses()
                    for feature in feature_classes + feature_tables:
                        if arcpy.Exists(feature) and arcpy.Describe(feature).dataType == 'FeatureClass':
                            project_spatial_id = self.create_entry(directory_path, f"{directory_path}\{feature}")
                        
                    # Remove the gdb from the dirs list so it doesnt walk through    
                    dirs.remove(dir)
                
            for file in files:
                # Built full file path
                file_path = f"{root}\{file}"
                
                lowercase_file = file.lower()
                if lowercase_file.endswith(IGNORE_EXTENSIONS):
                    continue
                
                elif lowercase_file.endswith(LAYOUT_FILE_EXTENSIONS):
                    project_spatial_id = self.create_entry(file_path, file_path, entry_type='Aspatial', processed=True)
                    
                    # Log it
                    log(self.params.log, Colors.WARNING, f'Layout file: {file_path} will be added to data tracker but not resulting gdb.', self.params.suppress, ps_script=self.params.ps_script, project_id=project_spatial_id)    
                
                elif lowercase_file.endswith(DATA_SHEET_EXTENSIONS):
                    project_spatial_id = self.create_entry(file_path, file_path, entry_type='Aspatial', processed=True)
                                        
                    # Log it
                    log(self.params.log, Colors.WARNING, f'Datasheet: {file_path} will be added to data tracker but not resulting gdb.', self.params.suppress, ps_script=self.params.ps_script, project_id=project_spatial_id)
                                                            
                elif lowercase_file.endswith(IMAGE_FILE_EXTENSIONS):
                    if lowercase_file.endswith('.pdf'):
                        project_spatial_id = self.create_entry(file_path, file_path, contains_pdf=True, entry_type='Aspatial', processed=True)                
                    else:
                        project_spatial_id = self.create_entry(file_path, file_path, contains_image=True, entry_type='Aspatial', processed=True)
                                           
                    # Log it
                    log(self.params.log, Colors.WARNING, f'Image/PDF file: {file_path} will be added to data tracker but not resulting gdb.', self.params.suppress, ps_script=self.params.ps_script, project_id=project_spatial_id)
                     
                elif lowercase_file.endswith('.shp'):
                    project_spatial_id = self.create_entry(file_path, file_path)
                      
                elif lowercase_file.endswith(('.kml', '.kmz')):
                    # Remove cascading styles from KML content
                    altered_file = file_path
                    if file.endswith('.kml'):
                        altered_file = self.remove_cascading_style(file_path)

                    # Check if the geodatabase exists
                    output_gdb = os.path.join(self.params.local_dir, "kml_layer.gdb")
                    if arcpy.Exists(output_gdb):
                        arcpy.management.Delete(output_gdb)
                        arcpy.management.Delete(output_gdb.replace('.gdb', '.lyrx'))

                    # Convert modified KML to layer and copy to geodatabase
                    arcpy.conversion.KMLToLayer(altered_file, self.params.local_dir, "kml_layer", "NO_GROUNDOVERLAY")   
                    
                    # Make the workspace the output gdb in the temp folder
                    arcpy.env.workspace = os.path.join(self.params.local_dir, "kml_layer.gdb", 'Placemarks')
                    
                    # Iterate through the feature classes and rename them
                    feature_classes = arcpy.ListFeatureClasses()
                    if feature_classes is None:
                        project_spatial_id = self.create_entry(file_path, file_path, processed=True)
                        
                        log(self.params.log, Colors.ERROR, f'The kml file {file_path} does not have any features', ps_script=self.params.ps_script)
                        
                        continue
                    
                    #
                    kml_gdb_path = os.path.join(self.params.local_dir, "KMLVault.gdb")
                    if not arcpy.Exists(kml_gdb_path):
                        arcpy.management.CreateFileGDB(self.params.local_dir, "KMLVault.gdb")

                    #                    
                    for feature in feature_classes:
                        project_spatial_id = self.create_entry(file_path, f"{file_path}\{feature}")
                        
                        arcpy.conversion.ExportFeatures(
                            os.path.join(arcpy.env.workspace, feature),
                            f"{kml_gdb_path}\proj_{project_spatial_id}"
                        )
                        
                elif lowercase_file.endswith('.geojson'):
                    project_spatial_id = self.create_entry(file_path, file_path)
                    
                elif lowercase_file.endswith(('.gpkg', '.sqlite')):
                    project_spatial_id = self.create_entry(file_path, file_path, processed=True)
                                        
                    # Log it
                    log(self.params.log, Colors.WARNING, f'GeoPackage/SQLite file: {file_path} will be added to data tracker but not resulting gdb.', self.params.suppress, ps_script=self.params.ps_script, project_id=project_spatial_id)
                    
                else:                    
                    # Log it
                    log(self.params.log, Colors.WARNING, f'Unsupported Filetype: {file_path} has been found and logged but not added to the datatracker or the geodatabase because it is not implemented or supported.', self.params.suppress, ps_script=self.params.ps_script)
    
    def create_entry(self, absolute_path: str, feature_path: str, in_raw_gdb: bool = False, contains_pdf: bool = False, contains_image: bool = False, entry_type: str = 'Spatial', processed: bool = False) -> str:
        """
        Creates a new entry in the data dictionary for spatial data processing.

        This function generates a unique project spatial ID, formats the paths, processes raw data matching, and adds the entry to the data dictionary with the given attributes.

        Args:
            absolute_path (str): The absolute path of the input file.
            feature_path (str): The path to the feature data.
            in_raw_gdb (bool): Indicates if the data is in the raw geodatabase format. Default is False.
            contains_pdf (bool): Indicates if the entry contains a PDF. Default is False.
            contains_image (bool): Indicates if the entry contains an image. Default is False.
            entry_type (str): The type of entry (e.g., 'Spatial'). Default is 'Spatial'.
            processed (bool): Indicates if the entry has been processed. Default is False.

        Returns:
            str: The formatted project spatial ID.
        """
        # Check project numbers and format the result
        formatted_result = self.check_project_numbers(feature_path)
        formatted_result = formatted_result.upper()

        # Create a unique identifier for the project spatial ID
        formatted_project_spatial_id = self.data.create_project_spatial_id(formatted_result)

        # Print file information if debugging is enabled
        if self.params.debug:
            log(None, Colors.INFO, feature_path)
            log(None, Colors.INFO, formatted_project_spatial_id)

        # Convert the raw data path to a relative path           
        raw_data_path = os.path.relpath(feature_path, self.params.output)
        
        # Convert the absolute path to the correct drive path format
        absolute_file_path = convert_drive_path(absolute_path)

        # Call a method to process raw data matching
        self.call_raw_data_match(formatted_project_spatial_id, raw_data_path)
                
        # Add data to the data class 
        self.data.add_data(
            project_spatial_id=formatted_project_spatial_id,
            project_number=formatted_result, 
            dropped=False,
            raw_data_path=raw_data_path, 
            raw_gdb_path=convert_drive_path(self.params.gdb_path),
            absolute_file_path=absolute_file_path,
            in_raw_gdb=in_raw_gdb, 
            contains_pdf=contains_pdf, 
            contains_image=contains_image,
            extracted_attachments_path=None,
            editor_tracking_enabled=False,
            processed=processed, 
            entry_type=entry_type
        )
        
        return formatted_project_spatial_id
      
    def process_entries(self) -> None:
        """
        Processes spatial data entries from a dictionary, converts them into a geodatabase format, and enables version control and editor tracking.

        The function iterates over the entries in the data dictionary, checks their file types, converts them to a geodatabase feature class, and updates their processing status.

        Args:
            None

        Returns:
            None
        """
        # Iterate over each entry in the data dictionary
        for index, entry in enumerate(self.data.data_dict):
            # Get the absolute path of the entry file
            entry_absolute_path:str = self.data.data_dict[entry].get('absolute_file_path')
            try:
                # Check if the current entry has already been processed
                if self.data.data_dict[entry].get('processed'):
                    continue
                
                # Define the name of the geodatabase entry and build path for the feature class in the local geodatabase 
                gdb_entry_name = f"proj_{entry}"
                feature_gdb_path = os.path.join(self.params.local_gdb_path, gdb_entry_name)
                
                # Check the file type and export features accordingly
                if entry_absolute_path.endswith('.gdb'):
                    # Export features from one geodatabase to the output geodatabase
                    arcpy.conversion.ExportFeatures(
                        self.params.output + self.data.data_dict[entry].get('raw_data_path'),
                        feature_gdb_path
                    )

                elif entry_absolute_path.endswith('.shp'):
                    # Export features from shapefile to the output geodatabase
                    arcpy.conversion.ExportFeatures(
                        entry_absolute_path,
                        feature_gdb_path
                    )
                                    
                elif entry_absolute_path.endswith(('.kml', '.kmz')):
                    # Export features from the KML/KMZ Vault geodatabase to the output geodatabase
                    arcpy.conversion.ExportFeatures(
                        os.path.join(self.params.local_dir, "KMLVault.gdb", gdb_entry_name),
                        feature_gdb_path
                    )
                
                elif entry_absolute_path.endswith('.geojson'):
                    # Export features from GeoJSON to the output geodatabase
                    arcpy.conversion.JSONToFeatures(
                        entry_absolute_path,
                        feature_gdb_path
                    )
                    
                # Update the entry status to indicate it has been processed and exists in raw geodatabase format
                self.data.set_data(
                    project_spatial_id=entry, 
                    in_raw_gdb=True,
                    processed=True
                )
                
                # Enable the version control of the layer in the geodatabase
                self.enable_version_control(feature_gdb_path)
                
                # Update the entry status to indicate that editor tracking is enabled
                self.data.set_data(
                    project_spatial_id=entry, 
                    editor_tracking_enabled=True
                )
            except (arcpy.ExecuteError, arcgisscripting.ExecuteError) as error:
                log(self.params.log, Colors.ERROR, f'An error occurred when processing the layer for {entry_absolute_path}, you can fix or remove it from the datatracker/database, then run the command again with --resume\n{error}', ps_script=self.params.ps_script, project_id=entry)
                # Can remove the comment from below when being shipped so the tool stops when a excetption is caught instead of continue on
                # raise Exception(error) 
            except Exception as error:
                log(self.params.log, Colors.ERROR, f'An uncaught error occurred when processing the layer for {entry_absolute_path}', ps_script=self.params.ps_script, project_id=entry)
                raise Exception(error)
      
    def search_for_spatial_data(self) -> None:
        """
        Walk through the directory structure and extract any spatial or data sheet file paths.

        Populates the `spatial_files` list with file paths.
        """
        # Step through unzip output path and keep track of paths
        for root, dirs, files in os.walk(self.params.output):
            for dir in dirs:
                # Skip over the gdb if tool is running a second time if it is somehow in the folder
                if dir is self.params.gdb_path:
                    continue
                if dir.endswith('.gdb'):
                    self.spatial_files.append(os.path.join(root, dir))
                    dirs.remove(dir) # Exclude .gdb directory from further recursion
            for file in files:
                file = file.lower()
                if file.endswith(SPATIAL_FILE_EXTENSIONS) or file.endswith(DATA_SHEET_EXTENSIONS) or file.endswith(LAYOUT_FILE_EXTENSIONS) or file.endswith(IMAGE_FILE_EXTENSIONS):
                    self.spatial_files.append(os.path.join(root, file))   
            
    def process_spatial_files(self) -> None:
        """Process all of the found spatial files."""
        for file in self.spatial_files:
            # Check project numbers and format the result
            formatted_result = self.check_project_numbers(file)
            formatted_result = formatted_result.upper()

            # Create a unique identifier for the project spatial ID
            formatted_project_spatial_id = self.data.create_project_spatial_id(formatted_result)

            # Print file information if debugging is enabled
            if self.params.debug:
                log(None, Colors.INFO, file)
                log(None, Colors.INFO, formatted_project_spatial_id)

            # Convert the raw data path to a relative path           
            raw_data_path = os.path.relpath(file, self.params.output)
            absolute_file_path = convert_drive_path(file)

            # Call a method to process raw data matching
            self.call_raw_data_match(formatted_project_spatial_id, raw_data_path)
            
            # Try to find if the entry is already in the tracker, skip if so
            if self.params.resume:
                (_, data_entry) = self.data.find_matching_data(absolute_file_path=absolute_file_path, processed=True)
                if data_entry:
                    continue
            
            # Add data to the data class 
            self.data.add_data(
                project_spatial_id=formatted_project_spatial_id,
                project_number=formatted_result, 
                dropped=False,
                raw_data_path=raw_data_path, 
                raw_gdb_path=convert_drive_path(self.params.gdb_path),
                absolute_file_path=absolute_file_path,
                in_raw_gdb=False, 
                contains_pdf=False, 
                contains_image=False,
                extracted_attachments_path=None,
                editor_tracking_enabled=False,
                processed=False, 
                entry_type='Spatial'
            )

            # Check the file type and call the appropriate processing method
            lowercase_file = file.lower()
            if lowercase_file.endswith(LAYOUT_FILE_EXTENSIONS):
                log(self.params.log, Colors.WARNING, f'Layout file: {file} will be added to data tracker but not resulting gdb.', self.params.suppress, ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)
                self.data.set_data(project_spatial_id=formatted_project_spatial_id, entry_type='Aspatial')
            elif lowercase_file.endswith(DATA_SHEET_EXTENSIONS):
                log(self.params.log, Colors.WARNING, f'Datasheet: {file} will be added to data tracker but not resulting gdb.', self.params.suppress, ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)
                self.data.set_data(project_spatial_id=formatted_project_spatial_id, entry_type='Aspatial')
            elif lowercase_file.endswith(IMAGE_FILE_EXTENSIONS):
                log(self.params.log, Colors.WARNING, f'Image/PDF file: {file} will be added to data tracker but not resulting gdb.', self.params.suppress, ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)
                
                # Update data tracker based on specific file types
                if lowercase_file.endswith('.pdf'):
                    self.data.set_data(project_spatial_id=formatted_project_spatial_id, contains_pdf=True, entry_type='Aspatial')
                else:
                    self.data.set_data(project_spatial_id=formatted_project_spatial_id, contains_image=True, entry_type='Aspatial')
                    
            elif lowercase_file.endswith('.shp'):
                self.process_shp(file, formatted_project_spatial_id)         
            elif lowercase_file.endswith(('.kml', '.kmz')):
                self.process_kml(file, formatted_project_spatial_id)    
            elif lowercase_file.endswith('.geojson'):
                self.process_json(file, formatted_project_spatial_id)
            elif lowercase_file.endswith('.gdb'):
                self.process_gdb(file, formatted_project_spatial_id)
            elif lowercase_file.endswith(('.gpkg', '.sqlite')):
                log(self.params.log, Colors.WARNING, f'GeoPackage/SQLite file: {file} will be added to data tracker but not resulting gdb.', self.params.suppress, ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)

            self.data.set_data(project_spatial_id=formatted_project_spatial_id, processed=True)
                    
    def check_project_numbers(self, file_path: str) -> str:
        """
        Check project numbers against a master data sheet.

        Args:
            file_path (str): Filepath to check.            

        Returns:
            str: the formatted result for the project number of the spatial file path.
        """
        # Define a regular expression pattern to extract project numbers and search for pattern in file path
        pattern = r'(\d{4})[\s_–-]*([a-zA-Z]{3})[\s_–-]*(\d{3})'
        search = re.search(pattern, file_path)
        
        # If no match is found, log a warning and assign an arbitrary project number
        if not search:
            log(self.params.log, Colors.WARNING, f'Could not find a project number for: {file_path} - Giving it an arbitrary project number "0000 XXX - 000"', self.params.suppress, ps_script=self.params.ps_script)
            formatted_result = '0000 XXX - 000'
        else:
            # Format the result using the matched groups
            formatted_result = '{} {} - {}'.format(search.group(1), search.group(2), search.group(3))

            # Check if the project number is in the project numbers list
            project_found = None
            for project_number in self.params.project_numbers:
                if project_number.lower().replace(' ', '') == formatted_result.lower().replace(' ', ''):
                    # Exit the loop as soon as the first occurrence is found
                    project_found = project_number
                    break

            if not project_found:
                log(self.params.log, Colors.WARNING, f'The project number {formatted_result} does not match any know project number in the master datasheet', self.params.suppress, ps_script=self.params.ps_script)
            
        return formatted_result
        
    def call_raw_data_match(self, current_spatial_id: str, raw_data_path: str) -> None:
        """
        Call the method that finds a matching raw data path and returns the project spatial id.

        Args:
            current_spatial_id (str): The current spatial project id being checked.
            raw_data_path (str): The raw data path to be searched in the dictionary.
        """
        # Find a corresponding project spatial ID in the data dictionary based on the raw data path
        (found_match, _) = self.data.find_matching_data(raw_data_path=raw_data_path)
        if found_match is not None:
            log(self.params.log, Colors.WARNING, f'Raw path: {raw_data_path} already exists in the data tracker! -  Current Spatial ID: {current_spatial_id} Matching Spatial ID: {found_match}', self.params.suppress, ps_script=self.params.ps_script, project_id=current_spatial_id)    

    def process_shp(self, file: str, formatted_project_spatial_id: str) -> None:
        """
        Process shapefiles.

        Args:
            file (str): Path to the shapefile.
            formatted_project_spatial_id (str): Formatted project spatial ID.
        """
        try:
            # Export features from shapefile to a geodatabase
            arcpy.conversion.ExportFeatures(
                file,
                self.params.local_gdb_path + f'\proj_{formatted_project_spatial_id}'
            )
            
            # Enable the version control of the layer in the geodatabase
            self.enable_version_control(self.params.local_gdb_path + f'\proj_{formatted_project_spatial_id}')
            
            # Change the flag to indicate it was succefully put into the Geodatabase
            self.data.set_data(
                project_spatial_id=formatted_project_spatial_id, 
                in_raw_gdb=True
            )
        except (arcpy.ExecuteError, arcgisscripting.ExecuteError) as error:
            log(self.params.log, Colors.ERROR, f'An error occurred when processing the layer for {file}, you can fix or remove it from the datatracker/database, then run the command again with --resume\n{error}', ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)
            # Can remove the comment from below when being shipped so the tool stops when a excetption is caught instead of continue on
            # raise Exception(error) 
        except Exception as error:
            log(self.params.log, Colors.ERROR, f'An uncaught error occurred when processing the layer for {file}', ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)
            raise Exception(error)
    
    def process_kml(self, file: str, formatted_project_spatial_id: str) -> None: 
        """
        Process KML/KMZ files.

        Args:
            file (str): Path to the KML/KMZ file.
            formatted_project_spatial_id (str): Formatted project spatial ID.
        """
        try:
            # Create temporary directory if it doesn't exist, otherwise, recreate it
            if not os.path.exists(self.temp_directory):
                os.makedirs(self.temp_directory)
            else:
                shutil.rmtree(self.temp_directory)
                os.makedirs(self.temp_directory)

            # Remove cascading styles from KML content
            altered_file = file
            if file.endswith('.kml'):
                altered_file = self.remove_cascading_style(file)

            # Convert modified KML to layer and copy to geodatabase
            arcpy.conversion.KMLToLayer(altered_file, self.temp_directory, "kml_layer", "NO_GROUNDOVERLAY")   
            
            # Make the workspace the output gdb in the temp folder
            arcpy.env.workspace = os.path.join(self.temp_directory, 'kml_layer.gdb/Placemarks')
            
            # Set starting raw data path and a flag for skipping first iteration
            base_raw_data_path = self.data.get_data(formatted_project_spatial_id)['raw_data_path']
            first_feature_class_processed = False
            
            # Iterate through the feature classes and rename them
            feature_classes = arcpy.ListFeatureClasses()
            if feature_classes is None:
                log(self.params.log, Colors.ERROR, f'The kml file {file} does not have any features', ps_script=self.params.ps_script)
                self.data.set_data(
                    project_spatial_id=formatted_project_spatial_id,
                    processed=True
                )
                return
            for index, feature_class in enumerate(feature_classes):           
                if first_feature_class_processed:
                    # Get data for the current feature and create a new project spatial ID
                    current_feature_data = self.data.get_data(formatted_project_spatial_id)
                    spatial_project_id = self.data.create_project_spatial_id(current_feature_data['project_number'])
                    
                    # Add data for the new project spatial ID
                    self.data.add_data(
                        project_spatial_id=spatial_project_id,
                        project_number=current_feature_data['project_number'],
                        dropped=False,
                        absolute_file_path=convert_drive_path(file),    
                        raw_data_path=current_feature_data['raw_data_path'],
                        raw_gdb_path=convert_drive_path(self.params.gdb_path),
                        in_raw_gdb=False,
                        contains_pdf=False,
                        contains_image=False,
                        extracted_attachments_path=None,
                        editor_tracking_enabled=False,
                        processed=False, 
                        entry_type='Spatial'
                    )
                    
                    # Update the formatted project spatial ID
                    formatted_project_spatial_id = spatial_project_id
                
                # Create a new name and export feature class
                new_name = f"proj_{formatted_project_spatial_id}"
                arcpy.management.Copy(
                    os.path.join(self.temp_directory, f'kml_layer.gdb/Placemarks/{feature_class}'),
                    os.path.join(self.params.local_gdb_path, new_name)
                )   
                
                # Enable the version control of the layer in the geodatabase
                self.enable_version_control(os.path.join(self.params.local_gdb_path, new_name))
                
                # Set the flag to indicate that the first feature class has been processed
                first_feature_class_processed = True
                
                new_raw_data_path = os.path.join(base_raw_data_path, feature_class)
                self.call_raw_data_match(formatted_project_spatial_id, new_raw_data_path)
                
                # Update the entry of the Geodatabase feature class
                self.data.set_data(
                    project_spatial_id=formatted_project_spatial_id, 
                    raw_data_path=new_raw_data_path, 
                    in_raw_gdb=True,
                    processed=True
                )
        except (arcpy.ExecuteError, arcgisscripting.ExecuteError) as error:
            log(self.params.log, Colors.ERROR, f'An error occurred when processing the layer for {file}, you can fix or remove it from the datatracker/database, then run the command again with --resume\n{error}', ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)
            # Can remove the comment from below when being shipped so the tool stops when a excetption is caught instead of continue on
            # raise Exception(error) 
        except Exception as error:
            log(self.params.log, Colors.ERROR, f'An uncaught error occurred when processing the layer for {file}', ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)
            raise Exception(error)
            
    def remove_cascading_style(self, file: str) -> str:
        """
        Remove cascading styles from KML-XML.
        
        Args:
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
        
        # Use regular expression to remove content between <Document and >
        kml_content = re.sub(r'<Document[^>]*>', '<Document>', kml_content)
        
        root = ET.fromstring(kml_content)
        cascading_styles = root.findall(".//{http://www.google.com/kml/ext/2.2}CascadingStyle")

        for cascading_style in cascading_styles:
            parent = root.find(".//{http://www.opengis.net/kml/2.2}Document")
            parent.remove(cascading_style)

        # Write modified KML content to a new file
        kml_output_no_gx_path = os.path.join(self.temp_directory, 'KMLWithoutGX.kml')
        ET.ElementTree(root).write(kml_output_no_gx_path, encoding="utf-8", xml_declaration=True)

        return kml_output_no_gx_path  
    
    def process_json(self, file: str, formatted_project_spatial_id: str) -> None:
        """
        Process GeoJSON files.

        Args:
            file (str): Path to the GeoJSON file.
            formatted_project_spatial_id (str): Formatted project spatial ID.
        """
        try:
            # Export features from GeoJSON to a geodatabase
            arcpy.conversion.JSONToFeatures(
                file,
                self.params.local_gdb_path + f'\proj_{formatted_project_spatial_id}'
            )
            
            # Enable the version control of the layer in the geodatabase
            self.enable_version_control(self.params.local_gdb_path + f'\proj_{formatted_project_spatial_id}')
            
            # Change the flag to indicate it was succefully put into the Geodatabase
            self.data.set_data(
                project_spatial_id=formatted_project_spatial_id, 
                in_raw_gdb=True
            )
        except (arcpy.ExecuteError, arcgisscripting.ExecuteError) as error:
            log(self.params.log, Colors.ERROR, f'An error occurred when processing the layer for {file}, you can fix or remove it from the datatracker/database, then run the command again with --resume\n{error}', ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)
            # Can remove the comment from below when being shipped so the tool stops when a excetption is caught instead of continue on
            # raise Exception(error) 
        except Exception as error:
            log(self.params.log, Colors.ERROR, f'An uncaught error occurred when processing the layer for {file}', ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)
            raise Exception(error)
        
    def process_gdb(self, file: str, formatted_project_spatial_id: str) -> None:
        """
        Process GeoDatabase files.

        Args:
            file (str): Path to the GeoDatabase file.
            formatted_project_spatial_id (str): Formatted project spatial ID.
        """
        try:
            # Set the workspace to the specified .gdb
            arcpy.env.workspace = file
            
            # Set starting raw data path and a flag for skipping first iteration because it was added in the process_spatial_files function
            base_raw_data_path = self.data.get_data(formatted_project_spatial_id)['raw_data_path']
            first_feature_class_processed = False
            
            # Iterate through the feature classes and tables
            feature_tables = arcpy.ListTables()
            feature_classes = arcpy.ListFeatureClasses()
            for feature in feature_classes + feature_tables:
                if first_feature_class_processed:
                    # Get data for the current feature and create a new project spatial ID
                    current_feature_data = self.data.get_data(formatted_project_spatial_id)
                    spatial_project_id = self.data.create_project_spatial_id(current_feature_data['project_number'])

                    # Add data for the new project spatial ID
                    self.data.add_data(
                        project_spatial_id=spatial_project_id,
                        project_number=current_feature_data['project_number'],
                        dropped=False,
                        raw_data_path=current_feature_data['raw_data_path'],
                        raw_gdb_path=convert_drive_path(self.params.gdb_path),
                        absolute_file_path=convert_drive_path(file),
                        in_raw_gdb=False,
                        contains_pdf=False,
                        contains_image=False,
                        extracted_attachments_path=None,
                        editor_tracking_enabled=False,
                        processed=False, 
                        entry_type='Spatial'
                    )
                    
                    # Update the formatted project spatial ID
                    formatted_project_spatial_id = spatial_project_id
                
                if arcpy.Exists(feature) and arcpy.Describe(feature).dataType == 'FeatureClass':
                    # Create a new name and export feature class
                    new_name = f"proj_{formatted_project_spatial_id}"
                    arcpy.conversion.ExportFeatures(
                        os.path.join(file, feature),
                        os.path.join(self.params.local_gdb_path, new_name)
                    )
                    
                    # Enable the version control of the layer in the geodatabase
                    self.enable_version_control(os.path.join(self.params.local_gdb_path, new_name))
                    
                    # Update the entry of the Geodatabase feature class
                    self.data.set_data(
                        project_spatial_id=formatted_project_spatial_id, 
                        in_raw_gdb=True,
                        processed=True,
                        entry_type='Spatial'
                    )
                
                # Set the flag to indicate that the first feature class has been processed
                first_feature_class_processed = True
                
                new_raw_data_path = os.path.join(base_raw_data_path, feature)
                self.call_raw_data_match(formatted_project_spatial_id, new_raw_data_path)
                
                # Update the entry of the Geodatabase feature class
                self.data.set_data(
                    project_spatial_id=formatted_project_spatial_id, 
                    raw_data_path=new_raw_data_path
                )
                
        except (arcpy.ExecuteError, arcgisscripting.ExecuteError) as error:
            log(self.params.log, Colors.ERROR, f'An error occurred when processing the layer for {file}, you can fix or remove it from the datatracker/database, then run the command again with --resume\n{error}', ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)
            # Can remove the comment from below when being shipped so the tool stops when a excetption is caught instead of continue on
            # raise Exception(error) 
        except Exception as error:
            log(self.params.log, Colors.ERROR, f'An uncaught error occurred when processing the layer for {file}', ps_script=self.params.ps_script, project_id=formatted_project_spatial_id)
            raise Exception(error)

    def extract_attachments(self) -> None:
        """
        Call the GeoAttachmentSeeker module function to find, extract and note down any attachments in the result GDB.
        """        
        # Find and process attachments from the gdb
        attachment_dict = find_attachments(self.params.local_gdb_path, self.params.attachments)
        
        # Print file information if debugging is enabled
        if self.params.debug:
            log(None, Colors.INFO, attachment_dict)
        
        # Iterating through key-value pairs using items()
        for key, value in attachment_dict.items():
            # Update the entry of the Geodatabase feature class
            self.data.set_data(
                project_spatial_id=key.replace('proj_', ''), 
                # extracted_attachments_path=value
                extracted_attachments_path=os.path.join(self.params.gdb_path, value.replace(f"C:\LocalTwoBillionToolkit\\", ''))
            )
        
        # Log completion of this task
        log(None, Colors.INFO, 'All attachments have been extracted from the result Geodatabase.')
        
    def enable_version_control(self, feature_class) -> None:
        """
        Enable the editor tracking version control for a feature class in the Geodatabase.
        """
        try:
            # Set the arc environement to the resulting GDB
            arcpy.env.workspace = self.params.local_gdb_path
            
            # Add a site id for mapping in a later tool
            arcpy.management.AddField(
                feature_class, 
                'bt_site_id',
                'SHORT'               
            )
            
            # Enable the 4 fields for editor tracking
            arcpy.EnableEditorTracking_management(feature_class, "bt_created_by", "bt_date_created", "bt_last_edited_by", "bt_date_edited", "ADD_FIELDS", "UTC")
            
            # Set flag in data object for editor tracking to True
            self.data.set_data(
                project_spatial_id=os.path.basename(feature_class).replace('proj_', ''),
                editor_tracking_enabled=True
            )
        
        except Exception as error:
            log(self.params.log, Colors.ERROR, f'An error has been caught while trying to enable editor tracking for {feature_class} in resulting gdb, {error}', ps_script=self.params.ps_script)

        
def convert_drive_path(file_path):
    """
    Converts a path with a mapped drive (ie. M:\, V:\) to the actual network drive name.
    """
    abs_file_path = os.path.abspath(file_path)
    actual_drive_path = abs_file_path

    try:
        # Extract drive letter from absolute file path
        drive_letter, _ = os.path.splitdrive(abs_file_path)

        # Check if the path contains a drive letter
        if re.match(r"[A-Za-z]{1}:{1}", drive_letter):
            # Convert mapped drive path to UNC path
            actual_drive_path = win32wnet.WNetGetUniversalName(actual_drive_path, 1)
    except Exception as e:
        print(f"Error: {e}")

    return actual_drive_path