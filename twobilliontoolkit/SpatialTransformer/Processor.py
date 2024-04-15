# twobilliontoolkit/SpatialTransformer/Processor.py
#========================================================
# Imports
#========================================================
import arcpy
import re
import tempfile
import xml.etree.ElementTree as ET
import win32wnet
import arcgisscripting

from twobilliontoolkit.SpatialTransformer.common import *
from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.GeoAttachmentSeeker.geo_attachment_seeker import find_attachments
from twobilliontoolkit.SpatialTransformer.Datatracker import Datatracker2BT
from twobilliontoolkit.RecordReviser.record_reviser import call_record_reviser
from twobilliontoolkit.SpatialTransformer.Parameters import Parameters
from twobilliontoolkit.SpatialTransformer.network_transfer import transfer

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
              
    def search_for_spatial_data(self) -> None:
        """
        Walk through the directory structure and extract any spatial or data sheet file paths.

        Populates the `spatial_files` list with file paths.
        """
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
            
    def process_spatial_files(self) -> None:
        """Process all of the found spatial files."""
        for file in self.spatial_files:
            # Check project numbers and format the result
            formatted_result = self.check_project_numbers(file, self.params.masterdata)
            formatted_result = formatted_result.upper()

            # Create a unique identifier for the project spatial ID
            formatted_project_spatial_id = self.data.create_project_spatial_id(formatted_result)

            # Print file information if debugging is enabled
            if self.params.debug:
                log(None, Colors.INFO, file)
                log(None, Colors.INFO, formatted_project_spatial_id)

            # Convert the raw data path to a relative path and extract the project path            
            raw_data_path = os.path.relpath(file, self.params.output)
            project_path = raw_data_path.split("\\")[0]
            absolute_file_path = convert_to_actual_drive_path(file)

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
                project_path=project_path, 
                raw_data_path=raw_data_path, 
                absolute_file_path=absolute_file_path,
                in_raw_gdb=False, 
                contains_pdf=False, 
                contains_image=False,
                extracted_attachments_path=None,
                editor_tracking_enabled=False,
                processed=False
            )
            
            # 
            try:
                # Check the file type and call the appropriate processing method
                lowercase_file = file.lower()
                if lowercase_file.endswith(LAYOUT_FILE_EXTENSIONS):
                    log(self.params.log, Colors.WARNING, f'Layout file: {file} will be added to data tracker but not resulting gdb.', self.params.suppress)
                elif lowercase_file.endswith(DATA_SHEET_EXTENSIONS):
                    log(self.params.log, Colors.WARNING, f'Datasheet: {file} will be added to data tracker but not resulting gdb.', self.params.suppress)
                elif lowercase_file.endswith(IMAGE_FILE_EXTENSIONS):
                    log(self.params.log, Colors.WARNING, f'Image/PDF file: {file} will be added to data tracker but not resulting gdb.', self.params.suppress)
                    
                    # Update data tracker based on specific file types
                    if lowercase_file.endswith('.pdf'):
                        self.data.set_data(project_spatial_id=formatted_project_spatial_id, contains_pdf=True)
                    else:
                        self.data.set_data(project_spatial_id=formatted_project_spatial_id, contains_image=True)
                        
                elif lowercase_file.endswith('.shp'):
                    self.process_shp(file, formatted_project_spatial_id)         
                elif lowercase_file.endswith(('.kml', '.kmz')):
                    self.process_kml(file, formatted_project_spatial_id)    
                elif lowercase_file.endswith('.geojson'):
                    self.process_json(file, formatted_project_spatial_id)
                elif lowercase_file.endswith('.gdb'):
                    self.process_gdb(file, formatted_project_spatial_id)
                elif lowercase_file.endswith(('.gpkg', '.sqlite')):
                    log(self.params.log, Colors.WARNING, f'GeoPackage/SQLite file: {file} will be added to data tracker but not resulting gdb.', self.params.suppress)

                self.data.set_data(project_spatial_id=formatted_project_spatial_id, processed=True)
            
            except arcpy.ExecuteError as error:
                log(self.params.log, Colors.ERROR, f'An error occured when processing the layer for {file}: {error} You can fix or remove it from the datatracker/database, then run the command again with --resume')
            except arcgisscripting.ExecuteError as error:
                log(self.params.log, Colors.ERROR, f'An error occured when processing the layer for {file}: {error} You can fix or remove it from the datatracker/database, then run the command again with --resume')
            except Exception as error:
                log(self.params.log, Colors.ERROR, f'An uncaught error occured when processing the layer for {file}')
                raise Exception(error)
                 
        log(None, Colors.INFO, 'Processing of the files into the Geodatabase has completed.')

        # Extract attachments from the Geodatabase
        self.extract_attachments()
                    
        # Save the data tracker before returning
        self.data.save_data()

        # Move the local files to the specified output
        if self.params.output is not '':
            log(None, Colors.INFO, f'Transfering local output to {self.params.output}.')
            transfer(
                self.params.local_dir,
                self.params.output,
                [os.path.basename(self.params.gdb), os.path.basename(self.params.datatracker), os.path.basename(self.params.attachments), self.params.log[:-4] + '_WARNING.txt', self.params.log[:-4] + '_ERROR.txt'],
                self.params.log
            )
        
        # Open the record reviser
        call_record_reviser(self.data, self.params.gdb)
        
    def check_project_numbers(self, file_path: str, master_df: pd.DataFrame) -> str:
        """
        Check project numbers against a master data sheet.

        Args:
            file_path (str): Filepath to check.
            master_df (pd.Dataframe): Master data sheet as a pandas DataFrame.

        Returns:
            str: the formatted result for the project number of the spatial file path.
        """
        # Define a regular expression pattern to extract project numbers and search for pattern in file path
        pattern = r'(\d{4})[\s_–-]*([a-zA-Z]{3})[\s_–-]*(\d{3})'
        search = re.search(pattern, file_path)
        
        # If no match is found, log a warning and assign an arbitrary project number
        if not search:
            log(self.params.log, Colors.WARNING, f'Could not find a project number for: {file_path} - Giving it an arbitrary project number "0000 XXX - 000"', self.params.suppress)
            formatted_result = '0000 XXX - 000'
        else:
            # Format the result using the matched groups
            formatted_result = '{} {} - {}'.format(search.group(1), search.group(2), search.group(3))

        # Check if the project number is found in the master datasheet
        project_found = master_df['Project Number'].str.replace(' ', '').eq(formatted_result.replace(' ', '').upper()).any()
        if not project_found:
            log(self.params.log, Colors.WARNING, f'The project number does not match any in the master datasheet', self.params.suppress)
            
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
            log(self.params.log, Colors.WARNING, f'Raw path: {raw_data_path} already exists in the data tracker! -  Current Spatial ID: {current_spatial_id} Matching Spatial ID: {found_match}', self.params.suppress)    

    def process_shp(self, file: str, formatted_project_spatial_id: str) -> None:
        """
        Process shapefile.

        Args:
            file (str): Path to the shapefile.
            formatted_project_spatial_id (str): Formatted project spatial ID.
        """
        # Export features from shapefile to a geodatabase
        arcpy.conversion.ExportFeatures(
            file,
            self.params.gdb + f'\proj_{formatted_project_spatial_id}'
        )
        
        #
        self.enable_version_control(self.params.gdb + f'\proj_{formatted_project_spatial_id}')
        
        # Change the flag to indicate it was succefully put into the Geodatabase
        self.data.set_data(
            project_spatial_id=formatted_project_spatial_id, 
            in_raw_gdb=True
        )
    
    def process_kml(self, file: str, formatted_project_spatial_id: str) -> None: 
        """
        Process KML/KMZ files.

        Args:
            file (str): Path to the KML/KMZ file.
            formatted_project_spatial_id (str): Formatted project spatial ID.
        """
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
            log(self.params.log, Colors.ERROR, f'The kml file {file} does not have any features')
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
                    project_path=current_feature_data['project_path'],
                    absolute_file_path=convert_to_actual_drive_path(file),    
                    raw_data_path=current_feature_data['raw_data_path'],
                    in_raw_gdb=False,
                    contains_pdf=False,
                    contains_image=False,
                    extracted_attachments_path=None,
                    editor_tracking_enabled=False,
                    processed=False
                )
                
                # Update the formatted project spatial ID
                formatted_project_spatial_id = spatial_project_id
            
            # Create a new name and export feature class
            new_name = f"proj_{formatted_project_spatial_id}"
            arcpy.management.Copy(
                os.path.join(self.temp_directory, f'kml_layer.gdb/Placemarks/{feature_class}'),
                os.path.join(self.params.gdb, new_name)
            )   
            
            #
            self.enable_version_control(os.path.join(self.params.gdb, new_name))
            
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
        # Export features from GeoJSON to a geodatabase
        arcpy.conversion.JSONToFeatures(
            file,
            self.params.gdb + f'\proj_{formatted_project_spatial_id}'
        )
        
        #
        self.enable_version_control(self.params.gdb + f'\proj_{formatted_project_spatial_id}')
        
        # Change the flag to indicate it was succefully put into the Geodatabase
        self.data.set_data(
            project_spatial_id=formatted_project_spatial_id, 
            in_raw_gdb=True
        )
        
    def process_gdb(self, file: str, formatted_project_spatial_id: str) -> None:
        """
        Process GeoDatabase files.

        Args:
            file (str): Path to the GeoDatabase file.
            formatted_project_spatial_id (str): Formatted project spatial ID.
        """
        # Set the workspace to the specified .gdb
        arcpy.env.workspace = file
        
        # Set starting raw data path and a flag for skipping first iteration
        base_raw_data_path = self.data.get_data(formatted_project_spatial_id)['raw_data_path']
        # first_feature_class_processed = False
        
        # Iterate through the feature classes and tables
        feature_tables = arcpy.ListTables()
        feature_classes = arcpy.ListFeatureClasses()
        for feature in feature_classes + feature_tables:
            # if first_feature_class_processed:
            # Get data for the current feature and create a new project spatial ID
            current_feature_data = self.data.get_data(formatted_project_spatial_id)
            spatial_project_id = self.data.create_project_spatial_id(current_feature_data['project_number'])
            
            # Add data for the new project spatial ID
            self.data.add_data(
                project_spatial_id=spatial_project_id,
                project_number=current_feature_data['project_number'],
                dropped=False,
                project_path=current_feature_data['project_path'],
                raw_data_path=current_feature_data['raw_data_path'],
                absolute_file_path=convert_to_actual_drive_path(file),
                in_raw_gdb=False,
                contains_pdf=False,
                contains_image=False,
                extracted_attachments_path=None,
                editor_tracking_enabled=False,
                processed=False
            )
            
            # Update the formatted project spatial ID
            formatted_project_spatial_id = spatial_project_id
                
            if arcpy.Exists(feature) and arcpy.Describe(feature).dataType == 'FeatureClass':
                # Create a new name and export feature class
                new_name = f"proj_{formatted_project_spatial_id}"
                arcpy.conversion.ExportFeatures(
                    os.path.join(file, feature),
                    os.path.join(self.params.gdb, new_name)
                )
                
                #
                self.enable_version_control(os.path.join(self.params.gdb, new_name))
                
                # Update the entry of the Geodatabase feature class
                self.data.set_data(
                    project_spatial_id=formatted_project_spatial_id, 
                    in_raw_gdb=True,
                    processed=True
                )
            
            # # Set the flag to indicate that the first feature class has been processed
            # first_feature_class_processed = True
            
            new_raw_data_path = os.path.join(base_raw_data_path, feature)
            self.call_raw_data_match(formatted_project_spatial_id, new_raw_data_path)
            
            # Update the entry of the Geodatabase feature class
            self.data.set_data(
                project_spatial_id=formatted_project_spatial_id, 
                raw_data_path=new_raw_data_path
            )

    def extract_attachments(self) -> None:
        """
        Call the GeoAttachmentSeeker module function to find, extract and note down any attachments in the result GDB.
        """        
        # Find and process attachments from the gdb
        attachment_dict = find_attachments(self.params.gdb, self.params.attachments)
        
        # Print file information if debugging is enabled
        if self.params.debug:
            log(None, Colors.INFO, attachment_dict)
        
        # Iterating through key-value pairs using items()
        for key, value in attachment_dict.items():
            # Update the entry of the Geodatabase feature class
            self.data.set_data(
                project_spatial_id=key.replace('proj_', ''), 
                extracted_attachments_path=value
            )
        
        # Log completion of this task
        log(None, Colors.INFO, 'All attachments have been extracted from the result Geodatabase.')
        
    def enable_version_control(self, feature_class) -> None:
        """
        Enable the editor tracking version control for a feature class in the Geodatabase.
        """
        try:
            # Set the arc environement to the resulting GDB
            arcpy.env.workspace = self.params.gdb
            
            # Add a site id for mapping in a later tool
            arcpy.management.AddField(
                feature_class, 
                'bt_site_id',
                'SHORT'               
            )
            
            # Enable the 4 fields for editor tracking
            arcpy.EnableEditorTracking_management(feature_class, "bt_created_by", "bt_date_created", "bt_last_edited_by", "bt_date_edited", "ADD_FIELDS", "UTC")
        except Exception as error:
            log(self.params.log, Colors.ERROR, f'An error has been caught while trying to enable editor tracking for {feature_class} in resulting gdb, {error}')

        
def convert_to_actual_drive_path(file_path):
    abs_file_path = os.path.abspath(file_path)
    actual_drive_path = abs_file_path

    # If the path is already an actual drive path, use it directly
    if os.path.exists(abs_file_path) and os.path.splitdrive(abs_file_path)[0]:
        return abs_file_path

    try:
        # Convert mapped drive path to UNC path
        actual_drive_path = win32wnet.WNetGetUniversalName(abs_file_path, 1)
    except Exception as e:
        print(f"Error: {e}")

    return actual_drive_path