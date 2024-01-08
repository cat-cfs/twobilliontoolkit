import unittest
import os
import sys
import shutil
from tempfile import TemporaryDirectory

# Add the path to the ripple_unzipple module to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ripple_unzipple.ripple_unzipple import ripple_unzip  # absolute import

class TestRecursiveUnzip(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = TemporaryDirectory()
        self.input_path = "Data/TestFolder"
        self.output_path = os.path.join(self.temp_dir.name, 'output')
        self.log_path = os.path.join(self.temp_dir.name, 'log.txt')

    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_invalid_input_path(self):
        # Test invalid input path
        invalid_input_path = "Invalid/Path"
        self.assertFalse(os.path.exists(invalid_input_path), "Test setup issue: The specified path exists.")

        # Use assertRaises to check if ValueError is raised with the correct error message
        with self.assertRaises(ValueError) as context:
            ripple_unzip(invalid_input_path, self.output_path)

        # Check if the correct error message is raised
        expected_error_message = f"The specified path does not exist: {invalid_input_path}"
        self.assertEqual(str(context.exception), expected_error_message)
    
    def test_directory(self):
        # Test unzipping a directory
        ripple_unzip(self.input_path, self.output_path)
        self.assertTrue(os.path.exists(self.output_path))

    def test_archive_zip(self):
        # Test unzipping a .zip file
        ripple_unzip(self.input_path + '.zip', self.output_path)
        self.assertTrue(os.path.exists(self.output_path))

    def test_archive_7z(self):
        # Test unzipping a .7z file
        ripple_unzip(self.input_path +'.7z', self.output_path)
        self.assertTrue(os.path.exists(self.output_path))
        
    def test_unsupported(self):
        # Test unsupported input type
        unsupported_input_path = self.input_path + '.txt'

        # Use assertRaises to check if ValueError is raised with the correct error message
        with self.assertRaises(ValueError) as context:
            ripple_unzip(unsupported_input_path, self.output_path)
            
        expected_error_message = "Unsupported input type. Please provide a directory or a compressed file."
        self.assertEqual(str(context.exception), expected_error_message)
        
    def test_log_no_error(self):
        # Test logging when no errors occur
        ripple_unzip(self.input_path, self.output_path, self.log_path)

        # Assert that the log file does not exist when no errors occur
        self.assertFalse(os.path.exists(self.log_path))

    def test_log_with_error(self):
        # Test logging when an error occurs
        invalid_input_path = "Invalid/Path"

        # Use assertRaises to check if ValueError is raised with the correct error message
        with self.assertRaises(ValueError) as context:
            ripple_unzip(invalid_input_path, self.output_path, self.log_path)

        # Check if the correct error message is raised
        expected_error_message = f"The specified path does not exist: {invalid_input_path}"
        self.assertEqual(str(context.exception), expected_error_message)

        # Check if the log file is created and contains the expected error message
        self.assertTrue(os.path.exists(self.log_path))
        with open(self.log_path, 'r') as log_file:
            log_content = log_file.read()
        self.assertIn('[ERROR]', log_content)
        
    def test_recursive_unzip(self):
        # Test recursive unzipping within a directory
        # define some test paths to make sure the recursion worked
        path1 = '/TestFolder'
        path2 = '/TestFolder/Child 5.xlsx'
        path3 = '/TestFolder/Child 1/Child 1.5'
        path4 = '/TestFolder/Child 3/Child 3/Child 3.3.xlsx'
        path5 = '/TestFolder/Child 2/Child 2/Child 2.6/Child 2.6/Child 2.6.6/Child 2.6.6/Child 2.6.6.1.txt'

        # Test unzipping a .zip file
        ripple_unzip(self.input_path + '.zip', self.output_path)
        self.assertTrue(os.path.exists(self.output_path + path1))
        self.assertTrue(os.path.exists(self.output_path + path2))
        self.assertTrue(os.path.exists(self.output_path + path3))
        self.assertTrue(os.path.exists(self.output_path + path4))
        self.assertTrue(os.path.exists(self.output_path + path5))

        # Test unzipping a .7z file
        ripple_unzip(self.input_path +'.7z', self.output_path)
        self.assertTrue(os.path.exists(self.output_path + path1))
        self.assertTrue(os.path.exists(self.output_path + path2))
        self.assertTrue(os.path.exists(self.output_path + path3))
        self.assertTrue(os.path.exists(self.output_path + path4))
        self.assertTrue(os.path.exists(self.output_path + path5))

if __name__ == '__main__':
    unittest.main()
    