import unittest
import os
import sys
import shutil
from tempfile import TemporaryDirectory

from twobilliontoolkit.GeoAttachmentSeeker.geo_attachment_seeker import find_attachments, process_attachment 

class TestGeoAttachmentSeeker(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = TemporaryDirectory()
        self.input_path = "Testing/Data2"
        self.output_path = os.path.join(self.temp_dir.name, 'output')

    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_find_attachments(self):
        # Test finding attachment tables
        geodatabase = os.path.join(self.input_path, 'TestGDB1.gdb')
        result = find_attachments(geodatabase, self.output_path)
        self.assertTrue('proj_test1' in result.keys(), "proj_test1 in the 1st geodatabase was not found correctly.")
        self.assertTrue('proj_test2' in result.keys(), "proj_test2 in the 1st geodatabase was not found correctly.")
        self.assertTrue('proj_test3' in result.keys(), "proj_test3 in the 1st geodatabase was not found correctly.")
        self.assertFalse('proj_test4' in result.keys(), "proj_test4 was not in the 1st geodatabase but appeared in the dictionary.")
        
        geodatabase = os.path.join(self.input_path, 'TestGDB2.gdb')
        result = find_attachments(geodatabase, self.output_path)
        self.assertTrue('proj_test100' in result.keys(), "proj_test100 in the 2nd geodatabase was not found correctly.")
        self.assertFalse('proj_test100a' in result.keys(), "proj_test100a was in the second geodatabase, but was not an attach table.")
        self.assertFalse('proj_test1' in result.keys(), "proj_test1 was not in the 2nd geodatabase but appeared in the dictionary.")
        
        geodatabase = os.path.join(self.input_path, 'TestGDB3.gdb')
        result = find_attachments(geodatabase, self.output_path)
        self.assertFalse('proj_test10' in result.keys(), "proj_test10 was in the 3nd geodatabase but did not have corresponding attachments.")
        self.assertTrue('proj_test20' in result.keys(), "proj_test20 was in the 3nd geodatabase but was not found, it does not have a corresponding relation or layer file though.")
        self.assertFalse('proj_test30' in result.keys(), "proj_test30 was in the 3nd geodatabase but was just the relation between layer and attachments so should not be in the dictionary.")

    def test_processing_attachments(self):
        # Test processing/extracting of attachment tables
        geodatabase = os.path.join(self.input_path, 'TestGDB1.gdb')
        find_attachments(geodatabase, self.output_path)
        self.assertTrue(os.path.exists(os.path.join(self.output_path, 'proj_test1')), "proj_test1 attachments were not extracted to their path correctly.")
        self.assertTrue(os.path.exists(os.path.join(self.output_path, 'proj_test2')), "proj_test2 attachments were not extracted to their path correctly.")
        self.assertTrue(os.path.exists(os.path.join(self.output_path, 'proj_test3')), "proj_test3 attachments were not extracted to their path correctly.")
        
        geodatabase = os.path.join(self.input_path, 'TestGDB2.gdb')
        find_attachments(geodatabase, self.output_path)
        self.assertTrue(os.path.exists(os.path.join(self.output_path, 'proj_test100')), "proj_test100 attachments were not extracted to their path correctly.")
        
        geodatabase = os.path.join(self.input_path, 'TestGDB3.gdb')
        find_attachments(geodatabase, self.output_path)
        self.assertTrue(os.path.exists(os.path.join(self.output_path, 'proj_test20')), "proj_test20 attachments were not extracted to their path correctly.")

if __name__ == '__main__':
    unittest.main()
    