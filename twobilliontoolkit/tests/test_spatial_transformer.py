# Testing/test_spatial_transformer.py
#========================================================
# Imports
#========================================================
import unittest
import sys
import os

from twobilliontoolkit.SpatialTransformer.common import *
from twobilliontoolkit.SpatialTransformer.Parameters import Parameters
from twobilliontoolkit.SpatialTransformer.Processor import Processor
from twobilliontoolkit.SpatialTransformer.Datatracker import Datatracker

#========================================================
# Testing Class
#========================================================
class TestDataHandling(unittest.TestCase):

    def setUp(self) -> None:
        self.test_directory = '.\Testing\TestCases'
        os.makedirs(self.test_directory, exist_ok=True)
        
        input_path = '..\spatial_data_processing_workflow\TestData\DataTracker_SpatialData'
        output_path = os.path.join(self.test_directory,'TestResultData')
        gdb_path = os.path.join(self.test_directory,'TestResultGDB.gdb')
        datatracker_path = os.path.join(self.test_directory,'TestDataTracker.xlsx')
        log_path = os.path.join(self.test_directory,'TestResultLog.txt')
        debug = False
        
        self.startparams = Parameters(input_path, output_path, gdb_path, datatracker_path, log_path, debug)
        self.processor = Processor(self.startparams)
        self.datatracker = Datatracker(self.startparams.datatracker, load_from='datatracker', save_to='datatracker')
            
    def test_startup_parameters(self):
        # Test case for Parameters class initialization
        self.assertEqual(self.startparams.input, '..\spatial_data_processing_workflow\TestData\DataTracker_SpatialData')
        self.assertEqual(self.startparams.output, os.path.join(self.test_directory,'TestResultData'))
        self.assertEqual(self.startparams.gdb, os.path.join(self.test_directory,'TestResultGDB.gdb'))
        self.assertEqual(self.startparams.datatracker, os.path.join(self.test_directory,'TestDataTracker.xlsx'))
        self.assertEqual(self.startparams.log, os.path.join(self.test_directory,'TestResultLog.txt'))
        self.assertEqual(self.startparams.debug, False)

    def test_unzip(self):
        # Test case for running the unzip tool at the beginning
        self.startparams.handle_unzip()
        self.assertTrue(os.path.exists(self.startparams.output), f"Output Directory was not created successfully: {self.startparams.output}")

    def test_creating_gdb(self):
        # Test case for creating a geodatabase if not already exist
        self.startparams.create_gdb()
        self.assertTrue(os.path.exists(self.startparams.gdb), f"Geodatabase does not exist, so was not created correctly: {self.startparams.gdb}")
        
    def create_dummy_dir(self, dummy_files):
        # Create a dummy directory structure for testing
        dummy_root = os.path.join(os.getcwd(), 'Testing', 'TestCases', 'dummies')

        for file_path in dummy_files:
            # Ensure the directory structure exists
            directory_path = os.path.dirname(os.path.join(dummy_root, file_path))
            os.makedirs(directory_path, exist_ok=True)

            # Create a dummy file
            with open(os.path.join(dummy_root, file_path), 'w') as dummy_file:
                dummy_file.write("This is a dummy file content.")
                
    def test_search_for_spatial_data(self):
        # Test case for tesing the search spatial data method
        dummy_files = ['file1.shp', 'file2.kml', 'file3.pdf']
        self.create_dummy_dir(dummy_files)

        temp_params = Parameters(self.startparams.input, os.path.join(self.test_directory, 'dummies'), self.startparams.gdb, self.startparams.datatracker, self.startparams.log, False)
        temp_processor = Processor(temp_params)
        
        # Run the search_for_spatial_data method
        temp_processor.search_for_spatial_data()

        # Check if the spatial files list is populated correctly
        expected_spatial_files = [os.path.join(self.test_directory, 'dummies', file) for file in dummy_files]
        self.assertEqual(temp_processor.spatial_files, expected_spatial_files)
        
    def test_processing_files(self):
        # Test case for tesing processing the spatial files
        # Update the input path in the Parameters for testing
        temp_params = Parameters(self.startparams.input, os.path.join(self.test_directory,'..', 'input'), self.startparams.gdb, os.path.join(self.test_directory, 'datatracker2.xlsx'), self.startparams.log, False)
        temp_processor = Processor(temp_params)

        arcpy.env.workspace = self.startparams.gdb

        # Run the search_for_spatial_data method
        temp_processor.search_for_spatial_data()
        master_data_df = pd.read_excel(r".\Redacted_Master_Data.xlsx")
        temp_processor.process_spatial_files(master_data_df)

        arcpy.env.workspace = temp_processor.params.gdb

        self.assertTrue(arcpy.Exists('proj_0000_XXX_000_1')) 
        self.assertTrue(arcpy.Exists('proj_0000_XXX_000_2')) 
        self.assertTrue(arcpy.Exists('proj_0000_XXX_000_3')) 
        self.assertTrue(arcpy.Exists('proj_0000_XXX_000_4')) 
        self.assertTrue(arcpy.Exists('proj_0000_XXX_000_5')) 
   
    # def test_process_shp(self):
    #     # Test case for processing a shapefile        
    #     file = os.path.join(self.test_directory,'..', 'input', 'test.shp')
    #     formatted_project_spatial_id = '0001_XXX_000_1'
        
    #     if not arcpy.Exists(self.startparams.gdb):
    #         arcpy.management.CreateFileGDB(os.path.dirname(self.startparams.gdb), os.path.basename(self.startparams.gdb))

    #     # arcpy.env.workspace = self.startparams.gdb

    #     self.processor.process_shp(file, formatted_project_spatial_id, self.datatracker)
                
    #     self.assertTrue(arcpy.Exists('proj_0001_XXX_000_1')) 
    
    # def test_process_kml(self):
    #     # Test case for processing a kml
    #     file = os.path.join(self.test_directory,'..', 'input', 'test.kml')
    #     formatted_project_spatial_id = '0002_XXX_000_1'
        
    #     # Add data for the new project spatial ID
    #     self.datatracker.add_data(
    #         project_spatial_id=formatted_project_spatial_id,
    #         project_number='0002 XXX 000',
    #         project_path='path',
    #         raw_data_path='path',
    #         in_raw_gdb=False,
    #         contains_pdf=False,
    #         contains_image=False
    #     )
    
    #     if not arcpy.Exists(self.startparams.gdb):
    #         arcpy.management.CreateFileGDB(os.path.dirname(self.startparams.gdb), os.path.basename(self.startparams.gdb))
            
    #     self.processor.process_kml(file, formatted_project_spatial_id, self.datatracker)
                
    #     self.assertTrue(arcpy.Exists('proj_0002_XXX_000_1')) 
    
    # def test_process_geojson(self):
    #     # Test case for processing a geojson
    #     file = os.path.join(self.test_directory,'..', 'input', 'test.geojson')
    #     formatted_project_spatial_id = '0003_XXX_000_1'
        
    #     if not arcpy.Exists(self.startparams.gdb):
    #         arcpy.management.CreateFileGDB(os.path.dirname(self.startparams.gdb), os.path.basename(self.startparams.gdb))
        
    #     self.processor.process_json(file, formatted_project_spatial_id, self.datatracker)
                
    #     self.assertTrue(arcpy.Exists('proj_0003_XXX_000_1')) 
            
    # def test_process_gdb(self):
    #     # Test case for processing a gdb
    #     file = os.path.join(self.test_directory,'..', 'input', 'test.gdb')
    #     formatted_project_spatial_id = '0004_XXX_000_1'
            
    #     if not arcpy.Exists(self.startparams.gdb):
    #         arcpy.management.CreateFileGDB(os.path.dirname(self.startparams.gdb), os.path.basename(self.startparams.gdb))
            
    #     self.processor.process_gdb(file, formatted_project_spatial_id, self.datatracker)
                
    #     self.assertTrue(arcpy.Exists('proj_0004_XXX_000_1')) 
            
    def test_add_data(self):
        # Test the add_data method
        project_spatial_id = 1
        project_number = '0000 XXX - 111'
        project_path = '/path/to/project1'
        raw_data_path = '/path/to/raw/data1'

        # Add initial data
        self.datatracker.add_data(
            project_spatial_id=project_spatial_id, 
            project_number=project_number, 
            project_path=project_path, 
            raw_data_path=raw_data_path, 
            in_raw_gdb=False, 
            contains_pdf=False, 
            contains_image=False
        )

        # Check if the data was added correctly
        self.assertNotEqual(self.datatracker.get_data(project_spatial_id), None)
        self.assertEqual(self.datatracker.get_data(project_spatial_id)['project_number'], project_number)
        self.assertEqual(self.datatracker.get_data(project_spatial_id)['project_path'], project_path)
        self.assertEqual(self.datatracker.get_data(project_spatial_id)['raw_data_path'], raw_data_path)
        self.assertFalse(self.datatracker.get_data(project_spatial_id)['in_raw_gdb'])
        self.assertFalse(self.datatracker.get_data(project_spatial_id)['contains_pdf'])
        self.assertFalse(self.datatracker.get_data(project_spatial_id)['contains_image'])

    def test_set_data(self):
        # Test the set_data method
        project_spatial_id = 2
        project_number = '0000 XXX - 222'
        project_path = '/path/to/project2'
        raw_data_path = '/path/to/raw/data2'

        # Add initial data
        self.datatracker.add_data(
            project_spatial_id=project_spatial_id, 
            project_number=project_number, 
            project_path=project_path, 
            raw_data_path=raw_data_path, 
            in_raw_gdb=False, 
            contains_pdf=False, 
            contains_image=False
        )
        
        project_number = '0000 XXX - 222Set'
        raw_data_path = '/path/to/raw/data2Set'

        # Update the data
        self.datatracker.set_data(
            project_spatial_id=project_spatial_id, 
            project_number=project_number, 
            raw_data_path=raw_data_path
        )

        # Check if the data was updated correctly
        updated_data = self.datatracker.get_data(project_spatial_id)
        self.assertEqual(updated_data['project_number'], project_number)
        self.assertEqual(updated_data['raw_data_path'], raw_data_path)
        self.assertFalse(updated_data['in_raw_gdb'])

    def test_find_matching_spatial_id(self):
        # Test the find_matching_spatial_id method
        project_spatial_id = 3
        project_number = '0000 XXX - 333'
        project_path = '/path/to/project3'
        raw_data_path = '/path/to/raw/data3'

        # Test the method before adding the data
        matching_spatial_id = self.datatracker.find_matching_spatial_id(raw_data_path)
        self.assertIsNone(matching_spatial_id)

        # Add initial data
        self.datatracker.add_data(
            project_spatial_id=project_spatial_id, 
            project_number=project_number, 
            project_path=project_path, 
            raw_data_path=raw_data_path, 
            in_raw_gdb=False, 
            contains_pdf=False, 
            contains_image=False
        )

        # Test the method again
        matching_spatial_id = self.datatracker.find_matching_spatial_id(raw_data_path)
        self.assertIsNotNone(matching_spatial_id)
        self.assertEqual(matching_spatial_id, 3)

    def test_count_occurances(self):
        # Test the count_occurances method        
        project_spatial_id = 4
        project_number = '0000 XXX - 444'
        project_path = '/path/to/project4'
        raw_data_path = '/path/to/raw/data4'

        # Add initial data
        self.datatracker.add_data(
            project_spatial_id=project_spatial_id, 
            project_number=project_number, 
            project_path=project_path, 
            raw_data_path=raw_data_path, 
            in_raw_gdb=False, 
            contains_pdf=False, 
            contains_image=False
        )

        # Test the method
        occurrences = self.datatracker.count_occurances('project_number', project_number)
        self.assertEqual(occurrences, 1)
        
        # Add more entries with same project_number
        self.datatracker.add_data(
            project_spatial_id=44, 
            project_number=project_number, 
            project_path=project_path, 
            raw_data_path=raw_data_path, 
            in_raw_gdb=False, 
            contains_pdf=False, 
            contains_image=False
        )
        self.datatracker.add_data(
            project_spatial_id=444, 
            project_number=project_number, 
            project_path=project_path, 
            raw_data_path=raw_data_path, 
            in_raw_gdb=False, 
            contains_pdf=False, 
            contains_image=False
        )
        self.datatracker.add_data(
            project_spatial_id=4444, 
            project_number=project_number, 
            project_path=project_path, 
            raw_data_path=raw_data_path, 
            in_raw_gdb=False, 
            contains_pdf=False, 
            contains_image=False
        )
        
        # Test the method again
        occurrences = self.datatracker.count_occurances('project_number', project_number)
        self.assertEqual(occurrences, 4)

    def test_create_project_spatial_id(self):
        # Test the create_project_spatial_id method
        project_spatial_id = 5
        project_number = '0000 XXX - 555'
        project_path = '/path/to/project5'
        raw_data_path = '/path/to/raw/data5'
        
        # Test the method before addng the data, so it should be ..._1
        new_project_spatial_id = self.datatracker.create_project_spatial_id(project_number)
        self.assertEqual(new_project_spatial_id, '0000_XXX_555_1')

        # Add initial data
        self.datatracker.add_data(
            project_spatial_id=project_spatial_id, 
            project_number=project_number, 
            project_path=project_path, 
            raw_data_path=raw_data_path, 
            in_raw_gdb=False, 
            contains_pdf=False, 
            contains_image=False
        )
        
        # Add more data
        self.datatracker.add_data(
            project_spatial_id=55, 
            project_number=project_number, 
            project_path=project_path, 
            raw_data_path=raw_data_path, 
            in_raw_gdb=False, 
            contains_pdf=False, 
            contains_image=False
        )
        
        # Test the method again after adding two data entries, result should output ..._3 because it would be used for a third data entry
        new_project_spatial_id = self.datatracker.create_project_spatial_id(project_number)
        self.assertEqual(new_project_spatial_id, '0000_XXX_555_3')

    def test_load_and_save_data(self):
        # Test the load_data and _save_data methods
        project_spatial_id = 6
        project_number = '0000 XXX - 666'
        project_path = '/path/to/project6'
        raw_data_path = '/path/to/raw/data6'

        # Add initial data
        self.datatracker.add_data(
            project_spatial_id=project_spatial_id, 
            project_number=project_number, 
            project_path=project_path, 
            raw_data_path=raw_data_path, 
            in_raw_gdb=False, 
            contains_pdf=False, 
            contains_image=False
        )

        # Save and load data
        self.datatracker.save_data()

        # Create a new Datatracker instance to load the saved data
        loaded_data_tracker = Datatracker(self.startparams.datatracker)

        # Check if the data was loaded correctly
        loaded_data = loaded_data_tracker.get_data(project_spatial_id)
        self.assertEqual(loaded_data['project_number'], project_number)
        self.assertEqual(loaded_data['raw_data_path'], raw_data_path)
        self.assertFalse(loaded_data['in_raw_gdb'])
        self.assertFalse(loaded_data['contains_pdf'])
        self.assertFalse(loaded_data['contains_image'])
        
if __name__ == '__main__':
    unittest.main()
