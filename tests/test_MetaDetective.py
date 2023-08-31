import unittest
from collections import defaultdict, namedtuple
from io import StringIO
from unittest.mock import patch, Mock
import subprocess
import webbrowser
import sys
import os

test_folder = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(test_folder)
sys.path.append(parent_folder)
import MetaDetective as md

Args = namedtuple('Args', ['directory', 'files', 'type'])

class TestMetaDetective(unittest.TestCase):

    def setUp(self):
        self.sample_output = """
        ExifTool Version Number         : 10.80
        File Name                       : sample.jpg
        Directory                       : .
        File Type                       : JPEG
        File Type Extension             : jpg
        MIME Type                       : image/jpeg
        """
        self.expected_metadata = {
            "File Name": "sample.jpg",
            "File Type": "JPEG",
            "File Type Extension": "jpg"
        }

    @patch('subprocess.run')
    def test_exiftool_installed(self, mock_run):
        mock_run.return_value = Mock()
        try:
            md.check_exiftool_installed()
        except SystemExit as e:
            self.fail("check_exiftool_installed() raised SystemExit unexpectedly!")

    @patch('subprocess.run')
    def test_exiftool_not_installed(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(SystemExit) as cm:
            md.check_exiftool_installed()
        self.assertEqual(cm.exception.code, md.EXIFTOOL_NOT_INSTALLED)

    @patch('subprocess.run')
    def test_exiftool_execution_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
        with self.assertRaises(SystemExit) as cm:
            md.check_exiftool_installed()
        self.assertEqual(cm.exception.code, md.EXIFTOOL_EXECUTION_ERROR)

    @patch('subprocess.run')
    def test_get_metadata(self, mock_run):
        mock_result = Mock()
        mock_result.stdout = self.sample_output
        mock_run.return_value = mock_result

        result = md.get_metadata("sample.jpg", list(self.expected_metadata.keys()))

        self.assertDictEqual(result, self.expected_metadata)

    def test_matches_any_pattern_match_single(self):
        """Test when value matches a single pattern."""
        value = "Hello world"
        patterns = ["^Hello", "not present", "absent"]
        self.assertTrue(md.matches_any_pattern(value, patterns))

    def test_matches_any_pattern_no_match(self):
        """Test when value doesn't match any pattern."""
        value = "Hello world"
        patterns = ["not present", "absent", "missing"]
        self.assertFalse(md.matches_any_pattern(value, patterns))

    def test_matches_any_pattern_match_multiple(self):
        """Test when value matches multiple patterns."""
        value = "Hello world"
        patterns = ["^Hello", "world$", "llo"]
        self.assertTrue(md.matches_any_pattern(value, patterns))

    def test_matches_any_pattern_empty_patterns(self):
        """Test with an empty patterns list."""
        value = "Hello world"
        patterns = []
        self.assertFalse(md.matches_any_pattern(value, patterns))

    def test_matches_any_pattern_empty_value(self):
        """Test with an empty value."""
        value = ""
        patterns = ["^Hello", "not present", "absent"]
        self.assertFalse(md.matches_any_pattern(value, patterns))

    @patch('os.path.isdir', return_value=True)
    @patch('os.listdir', return_value=['file1.txt', 'file2.jpg', 'file3.png'])
    def test_get_files_from_directory_all_types(self, mock_listdir, mock_isdir):
        args = Args(directory='/mock_directory', files=None, type=['all'])
        result = md.get_files(args)
        self.assertEqual(result, [
            '/mock_directory/file1.txt',
            '/mock_directory/file2.jpg',
            '/mock_directory/file3.png'
        ])

    @patch('os.path.isdir', return_value=True)
    @patch('os.listdir', return_value=['file1.txt', 'file2.jpg', 'file3.png'])
    def test_get_files_from_directory_specific_type(self, mock_listdir, mock_isdir):
        args = Args(directory='/mock_directory', files=None, type=['jpg'])
        result = md.get_files(args)
        self.assertEqual(result, ['/mock_directory/file2.jpg'])

    @patch('os.path.isdir', return_value=False)
    def test_get_files_nonexistent_directory(self, mock_isdir):
        args = Args(directory='/nonexistent_directory', files=None, type=['all'])
        with self.assertRaises(SystemExit) as cm:
            md.get_files(args)
        self.assertIn("Error:", str(cm.exception))

    def test_get_files_no_directory(self):
        args = Args(directory=None, files=['/path/to/file1.txt', '/path/to/file2.jpg'], type=['all'])
        result = md.get_files(args)
        self.assertEqual(result, ['/path/to/file1.txt', '/path/to/file2.jpg'])

    @patch('os.path.isdir', return_value=True)
    @patch('os.listdir', return_value=[])
    def test_get_files_empty_directory(self, mock_listdir, mock_isdir):
        args = Args(directory='/empty_directory', files=None, type=['all'])
        with self.assertRaises(SystemExit) as cm:
            md.get_files(args)
        self.assertIn("Error: No files found.", str(cm.exception))
        
    def test_display_metadata_all(self):
        args = Mock(display='all', format='concise')
        metadata = [
            {"Field1": "Value1", "Field2": "Value2", "Field3": "Value3"},
            {"Field1": "Value4", "Field2": "Value5", "Field3": "Value6"}
        ]
        ignore_patterns = []
        
        expected_output = (
            "Field1: Value1\nField2: Value2\nField3: Value3\n"
            "----------------------------------------\n"
            "Field1: Value4\nField2: Value5\nField3: Value6\n"
            "----------------------------------------\n"
        )

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            md.display_metadata(args, metadata, ignore_patterns)
            self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('webbrowser.get')
    def test_open_browser_preferred_browser(self, mock_get):
        url = "https://www.example.com"
        preferred_browsers = ["chrome", "firefox"]
        
        mock_browser = mock_get.return_value
        mock_browser.open.return_value = True
        
        result = md.open_browser(url, preferred_browsers)
        
        self.assertTrue(result)
        mock_browser.open.assert_called_once_with(url)
    
    @patch('webbrowser.get')
    @patch('webbrowser.open')
    def test_open_browser_fallback(self, mock_open, mock_get):
        url = "https://www.example.com"
        preferred_browsers = ["chrome", "firefox"]
        
        mock_get.side_effect = [webbrowser.Error] * len(preferred_browsers)
        mock_open.return_value = True
        
        result = md.open_browser(url, preferred_browsers)
        
        self.assertTrue(result)
        mock_open.assert_called_once_with(url)

    @patch('webbrowser.get')
    @patch('webbrowser.open')
    def test_open_browser_failure(self, mock_open, mock_get):
        url = "https://www.example.com"
        preferred_browsers = ["chrome", "firefox"]
        
        mock_get.side_effect = [webbrowser.Error] * (len(preferred_browsers) + 1)
        mock_open.side_effect = webbrowser.Error
        
        result = md.open_browser(url, preferred_browsers)
        
        self.assertFalse(result)
        
if __name__ == "__main__":
    unittest.main()
