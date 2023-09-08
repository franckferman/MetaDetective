import unittest
from unittest.mock import patch, MagicMock
from MetaDetective import *

class TestMetaDetective(unittest.TestCase):

    def test_show_banner(self):
        with patch('builtins.print') as mocked_print:
            show_banner()
            mocked_print.assert_called_with(BANNER)

    def test_open_browser_successful(self):
        with patch('webbrowser.get') as mocked_get:
            browser = MagicMock()
            browser.open.return_value = True
            mocked_get.return_value = browser
            result = open_browser('https://example.com')
            self.assertTrue(result)

    def test_open_browser_failure(self):
        with patch('webbrowser.get') as mocked_get:
            browser = MagicMock()
            browser.open.return_value = False
            mocked_get.return_value = browser
            result = open_browser('https://example.com')
            self.assertFalse(result)

    def test_check_exiftool_installed_installed(self):
        with patch('subprocess.run') as mocked_run:
            # Create a MagicMock to simulate a successful run
            mock_run = unittest.mock.MagicMock()
            mock_run.return_value.returncode = 0
            mocked_run.return_value = mock_run
            
            try:
                check_exiftool_installed()
            except SystemExit as se:
                self.fail(f"check_exiftool_installed() raised SystemExit unexpectedly: {se}")

    def test_check_exiftool_installed_not_installed(self):
        with patch('subprocess.run') as mocked_run:
            mocked_run.side_effect = FileNotFoundError
            with self.assertRaises(SystemExit) as cm:
                check_exiftool_installed()
            self.assertEqual(str(cm.exception), 'Error: exiftool is not installed. Please install it to continue.')

    def test_check_exiftool_installed_execution_error(self):
        with patch('subprocess.run') as mocked_run:
            mocked_run.side_effect = subprocess.CalledProcessError(1, cmd="exiftool")
            with self.assertRaises(SystemExit) as cm:
                check_exiftool_installed()
            self.assertEqual(str(cm.exception), 'Error: exiftool encountered an error.')

    def test_dms_to_dd_North_East(self):
        degrees = 45
        minutes = 30
        seconds = 15.5
        direction = 'N'
        result = dms_to_dd(degrees, minutes, seconds, direction)
        expected_result = 45.504305555555556
        self.assertAlmostEqual(result, expected_result, places=6)

    def test_dms_to_dd_South_West(self):
        degrees = 45
        minutes = 30
        seconds = 15.5
        direction = 'S'
        result = dms_to_dd(degrees, minutes, seconds, direction)
        expected_result = -45.504305555555556
        self.assertAlmostEqual(result, expected_result, places=6)

    def test_dms_to_dd_Zero_Degrees(self):
        degrees = 0
        minutes = 0
        seconds = 0.0
        direction = 'N'
        result = dms_to_dd(degrees, minutes, seconds, direction)
        expected_result = 0.0
        self.assertEqual(result, expected_result)

    def test_parse_dms_valid(self):
        dms_str = "50 deg 49' 8.59\" N"
        result = parse_dms(dms_str)
        expected_result = (50, 49, 8.59, 'N')
        self.assertEqual(result, expected_result)

    def test_parse_dms_invalid(self):
        # Test parsing an invalid DMS string
        dms_str = "Invalid DMS string"
        result = parse_dms(dms_str)
        self.assertIsNone(result)

    def test_parse_dms_no_degrees(self):
        dms_str = "49' 8.59\" N"
        result = parse_dms(dms_str)
        self.assertIsNone(result)

    def test_parse_dms_no_minutes(self):
        dms_str = "50 deg 8.59\" N"
        result = parse_dms(dms_str)
        self.assertIsNone(result)

    def test_parse_dms_no_seconds(self):
        dms_str = "50 deg 49' N"
        result = parse_dms(dms_str)
        self.assertIsNone(result)

    def test_parse_dms_no_direction(self):
        dms_str = "50 deg 49' 8.59\""
        result = parse_dms(dms_str)
        self.assertIsNone(result)

    def test_get_metadata_valid(self):
        file_path = "valid_file.jpg"
        fields = ["Title", "Description", "GPS Position"]
        
        exiftool_output = """
            Title: Sample Title
            Description: This is a sample description
            GPS Position: 40 deg 30' 12.34\" N, 73 deg 59' 30.56\" W
        """
        with patch('subprocess.run') as mocked_run:
            mocked_run.return_value.stdout = exiftool_output
            result = get_metadata(file_path, fields)
        
        expected_result = {
            "Title": "Sample Title",
            "Description": "This is a sample description",
            "GPS Position": "40 deg 30' 12.34\" N, 73 deg 59' 30.56\" W",
            "Formatted GPS Position": "40.503428, -73.991822"
        }
        self.assertEqual(result, expected_result)

    def test_get_metadata_missing_fields(self):
        file_path = "missing_fields.jpg"
        fields = ["Title", "Description", "GPS Position"]
        
        exiftool_output = """
            Title: Sample Title
        """
        with patch('subprocess.run') as mocked_run:
            mocked_run.return_value.stdout = exiftool_output
            result = get_metadata(file_path, fields)
        
        expected_result = {
            "Title": "Sample Title"
        }
        self.assertEqual(result, expected_result)

    def test_get_metadata_no_gps(self):
        file_path = "no_gps.jpg"
        fields = ["Title", "Description", "GPS Position"]
        
        exiftool_output = """
            Title: Sample Title
            Description: This is a sample description
        """
        with patch('subprocess.run') as mocked_run:
            mocked_run.return_value.stdout = exiftool_output
            result = get_metadata(file_path, fields)
        
        expected_result = {
            "Title": "Sample Title",
            "Description": "This is a sample description"
        }
        self.assertEqual(result, expected_result)

    def test_matches_any_pattern_match(self):
        value = "Sample Text"
        patterns = ["sample", "test", "pattern"]
        result = matches_any_pattern(value, patterns)
        self.assertTrue(result)

    def test_matches_any_pattern_no_match(self):
        value = "Another Text"
        patterns = ["sample", "test", "pattern"]
        result = matches_any_pattern(value, patterns)
        self.assertFalse(result)

    def test_matches_any_pattern_empty_patterns(self):
        value = "Any Text"
        patterns = []
        result = matches_any_pattern(value, patterns)
        self.assertFalse(result)

    def test_matches_any_pattern_empty_value(self):
        value = ""
        patterns = ["sample", "test", "pattern"]
        result = matches_any_pattern(value, patterns)
        self.assertFalse(result)

    def test_get_files_directory_all_types(self):
        args = Namespace(directory="test_directory", type=['all'], files=[])
        
        with unittest.mock.patch('os.path.isdir', return_value=True), \
             unittest.mock.patch('os.listdir', return_value=['file1.txt', 'file2.jpg', 'file3.png']):
            result = get_files(args)
        
        expected_result = ['test_directory/file1.txt', 'test_directory/file2.jpg', 'test_directory/file3.png']
        self.assertEqual(result, expected_result)

    def test_get_files_directory_specific_type(self):
        args = Namespace(directory="test_directory", type=['jpg'], files=[])
        
        with unittest.mock.patch('os.path.isdir', return_value=True), \
             unittest.mock.patch('os.listdir', return_value=['file1.txt', 'file2.jpg', 'file3.png']):
            result = get_files(args)
        
        expected_result = ['test_directory/file2.jpg']
        self.assertEqual(result, expected_result)

    def test_get_files_nonexistent_directory(self):
        args = Namespace(directory="nonexistent_directory", type=['all'], files=[])
        
        with unittest.mock.patch('os.path.isdir', return_value=False):
            with self.assertRaises(SystemExit) as cm:
                get_files(args)
            self.assertEqual(cm.exception.code, f"Error: {args.directory} is not a directory.")

    def test_get_files_no_files_found(self):
        args = Namespace(directory="empty_directory", type=['all'], files=[])
        
        with unittest.mock.patch('os.path.isdir', return_value=True), \
             unittest.mock.patch('os.listdir', return_value=[]):
            with self.assertRaises(SystemExit) as cm:
                get_files(args)
            self.assertEqual(cm.exception.code, "Error: No files found.")

    def test_get_files_files_argument(self):
        args = Namespace(directory=None, type=['all'], files=['file1.txt', 'file2.jpg'])
        
        result = get_files(args)
        expected_result = ['file1.txt', 'file2.jpg']
        self.assertEqual(result, expected_result)

    def test_get_address_from_coords_valid(self):
        lat = "40.7128"
        lon = "-74.0060"
        
        with unittest.mock.patch('http.client.HTTPSConnection') as mocked_conn:
            mocked_response = unittest.mock.Mock()
            mocked_response.read.return_value = json.dumps({"display_name": "New York, USA"}).encode("utf-8")
            mocked_conn.return_value.getresponse.return_value = mocked_response
            result = get_address_from_coords(lat, lon)
        
        expected_result = "New York, USA"
        self.assertEqual(result, expected_result)

    def test_get_address_from_coords_error(self):
        lat = "40.7128"
        lon = "-74.0060"
        
        with unittest.mock.patch('http.client.HTTPSConnection', side_effect=Exception):
            result = get_address_from_coords(lat, lon)
        
        expected_result = ""
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
