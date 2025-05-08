import os
import unittest
from unittest.mock import Mock, patch
from twobilliontoolkit.SpatialTransformer.Datatracker import Datatracker, Datatracker2BT 

class TestDatatracker(unittest.TestCase):

    def setUp(self):
        self.temp_file = 'A:/2BT/02_Tools/twobilliontoolkit/twobilliontoolkit/tests/test_datatracker.xlsx'
        self.datatracker_f = Datatracker(self.temp_file, load_from='datatracker', save_to='datatracker')
        self.datatracker_d = Datatracker(self.temp_file, load_from='database', save_to='database')

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_initialization(self):
        self.assertIsNotNone(self.datatracker_f)
        self.assertIsNotNone(self.datatracker_d)

    def test_add_data(self):
        self.datatracker_f.add_data(key="key1", field1="value1", field2="test", field3=3)
        self.datatracker_f.add_data(key="key2", field1=False)
        self.assertEqual(self.datatracker_f.data_dict["key1"]["field1"], "value1")
        self.assertEqual(self.datatracker_f.data_dict["key1"]["field2"], "test")
        self.assertEqual(self.datatracker_f.data_dict["key1"]["field3"], 3)
        self.assertFalse(self.datatracker_f.data_dict["key2"]["field1"])

    def test_set_data(self):
        self.datatracker_f.add_data("key1", field1="value1", field2=True, field3=3)
        self.datatracker_f.set_data("key1", field1="value11", field3='updated')
        self.assertEqual(self.datatracker_f.data_dict["key1"]["field1"], "value11")
        self.assertTrue(self.datatracker_f.data_dict["key1"]["field2"])
        self.assertEqual(self.datatracker_f.data_dict["key1"]["field3"], "updated")

    def test_get_data(self):
        self.datatracker_f.add_data("key1", field1="value1")
        result = self.datatracker_f.get_data("key1")
        self.assertEqual(result["field1"], "value1")

    def test_find_matching_data(self):
        self.datatracker_f.add_data("key1", field1="value1", field2="value2")
        result = self.datatracker_f.find_matching_data(field1="value1", field2="value2")
        self.assertEqual(result[0], "key1")
        self.assertEqual(result[1]["field1"], "value1")

    def test_count_occurrences(self):
        self.datatracker_f.add_data("key1", field1="value1")
        self.datatracker_f.add_data("key2", field1="value1")
        result = self.datatracker_f.count_occurances("field1", "value1")
        self.assertEqual(result, 2)

    def test_save_and_load_to_file(self):
        # Add some data to the Datatracker instance
        self.datatracker_f.add_data(key='key1', field1='value1', field2='value2')
        
        # Save to a file
        self.datatracker_f.save_data()

        # Create a new Datatracker instance and load from the file
        new_datatracker_f = Datatracker(data_traker_path=self.temp_file, load_from='datatracker', save_to='datatracker')
        
        # Assert the loaded data
        loaded_data = new_datatracker_f.get_data(key='key1')
        self.assertEqual(loaded_data, {'field1': 'value1', 'field2': 'value2'})

class TestDatatracker2BT(unittest.TestCase):

    def setUp(self):
        self.temp_file = 'A:/2BT/02_Tools/twobilliontoolkit/twobilliontoolkit/tests/test_datatracker2.xlsx'
        self.datatracker2bt_f = Datatracker2BT(self.temp_file, load_from='datatracker', save_to='datatracker')
        self.datatracker2bt_d = Datatracker2BT(self.temp_file, load_from='database', save_to='database')

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_initialization(self):
        self.assertIsNotNone(self.datatracker2bt_f)
        self.assertIsNotNone(self.datatracker2bt_d)

    def test_add_data(self):
        self.datatracker2bt_f.add_data("spatial_id1", "123", False, "/path", "/raw_data", "/absolute_path", True, False, True, "/attachments", True, True)
        self.assertEqual(self.datatracker2bt_f.data_dict["spatial_id1"]["project_number"], "123")

    def test_set_data(self):
        self.datatracker2bt_f.add_data("spatial_id1", "123", False, "/path", "/raw_data", "/absolute_path", True, False, True, "/attachments", True, True)
        self.datatracker2bt_f.set_data("spatial_id1", project_number="456")
        self.assertEqual(self.datatracker2bt_f.data_dict["spatial_id1"]["project_number"], "456")

    def test_get_data(self):
        self.datatracker2bt_f.add_data("spatial_id1", "123", False, "/path", "/raw_data", "/absolute_path", True, False, True, "/attachments", True, True)
        result = self.datatracker2bt_f.get_data("spatial_id1")
        self.assertEqual(result["project_number"], "123")

    def test_find_matching_spatial_id(self):
        self.datatracker2bt_f.add_data("spatial_id1", "123", False, "/path", "/raw_data", "/absolute_path", True, False, True, "/attachments", True, True)
        result = self.datatracker2bt_f.find_matching_spatial_id("/raw_data")
        self.assertEqual(result, "spatial_id1")

    def test_create_project_spatial_id(self):
        self.datatracker2bt_f.add_data("spatial_id1", "123", False, "/path", "/raw_data", "/absolute_path", True, False, True, "/attachments", True, True)
        result = self.datatracker2bt_f.create_project_spatial_id("123")
        self.assertEqual(result, "123_02")

    def test_save_and_load_to_file(self):
        # Add some data to the Datatracker2BT instance
        self.datatracker2bt_f.add_data(
            project_spatial_id='proj3',
            project_number='101',
            dropped=False,
            raw_gdb_path='/path/to/gdb.gdb',
            absolute_file_path='/path/to/file3',
            in_raw_gdb=True,
            contains_pdf=False,
            contains_image=True,
            extracted_attachments_path='/path/to/attachments3',
            editor_tracking_enabled=False,
            processed=True
        )
        
        # Save to a file
        self.datatracker2bt_f.save_data()

        # Create a new Datatracker2BT instance and load from the file
        new_datatracker2bt_f = Datatracker2BT(data_traker_path=self.temp_file, load_from='datatracker', save_to='datatracker')
        
        # Assert the loaded data
        loaded_data = new_datatracker2bt_f.get_data(project_spatial_id='proj3')
        expected_data = {
            'project_number': '101',
            'dropped': False,
            'raw_gdb_path':'/path/to/gdb.gdb',
            'absolute_file_path': '/path/to/file3',
            'in_raw_gdb': True,
            'contains_pdf': False,
            'contains_image': True,
            'extracted_attachments_path': '/path/to/attachments3',
            'editor_tracking_enabled': False,
            'processed': True
        }
        self.assertEqual(loaded_data, expected_data)

if __name__ == '__main__':
    unittest.main()
