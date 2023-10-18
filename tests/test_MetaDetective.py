import json
import os
import re
import shutil
import subprocess
import sys
from io import StringIO
from typing import List
from unittest.mock import Mock, patch
import unittest

from src.MetaDetective.MetaDetective import (check_exiftool_installed, dms_to_dd, get_address_from_coords, 
                           get_files, get_metadata, matches_any_pattern, show_banner)


# Tests for show_banner
class TestShowBanner(unittest.TestCase):
    def setUp(self):
        self.held_output = StringIO()
        sys.stdout = self.held_output

    def tearDown(self):
        self.held_output.close()
        sys.stdout = sys.__stdout__

    def test_show_banner(self):
        show_banner()
        content = self.held_output.getvalue()
        self.assertTrue(isinstance(content, str))

# Tests for check_exiftool_installed
class TestExifToolCheck(unittest.TestCase):

    @patch('subprocess.run')
    def test_exiftool_installed(self, mock_run):
        mock_run.return_value = None
        try:
            check_exiftool_installed()
        except SystemExit as e:
            self.fail(f"Unexpected exit: {e}")

    @patch('subprocess.run')
    def test_exiftool_not_installed(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(SystemExit) as cm:
            check_exiftool_installed()
        self.assertEqual(cm.exception.code, "Error: exiftool is not installed. Please install it to continue.")

    @patch('subprocess.run')
    def test_exiftool_execution_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=['exiftool', '-ver'])
        with self.assertRaises(SystemExit) as cm:
            check_exiftool_installed()
        self.assertEqual(cm.exception.code, "Error: exiftool encountered an error.")

# Tests for dms_to_dd
class TestDmsToDd(unittest.TestCase):
    
    def test_dms_to_dd_north(self):
        result = dms_to_dd(51, 29, 46, 'N')
        self.assertAlmostEqual(result, 51.49611, 5)

    def test_dms_to_dd_south(self):
        result = dms_to_dd(51, 29, 46, 'S')
        self.assertAlmostEqual(result, -51.49611, 5)

# Tests for get_metadata
class TestGetMetadata(unittest.TestCase):

    def setUp(self):
        self.mocked_exiftool_output = """
        ExifTool Version Number         : 12.56
        File Name                       : test_MetaDetective-Franck_FERMAN.pdf
        Author                          : Franck FERMAN
        Last Modified By                : AHaibara
        Producer                        : PDFCreator 2.3.2.6
        """

    @patch("subprocess.run")
    def test_get_metadata(self, mock_run):
        mock_result = Mock()
        mock_result.stdout = self.mocked_exiftool_output
        mock_run.return_value = mock_result

        metadata = get_metadata("test_MetaDetective-Franck_FERMAN.pdf", ["File Name", "Author", "Last Modified By"])

        self.assertIn("File Name", metadata)
        self.assertEqual(metadata["File Name"], "test_MetaDetective-Franck_FERMAN.pdf")
        self.assertIn("Author", metadata)
        self.assertEqual(metadata["Author"], "Franck FERMAN")
        self.assertIn("Last Modified By", metadata)
        self.assertEqual(metadata["Last Modified By"], "AHaibara")

    @patch("subprocess.run")
    def test_get_metadata_with_gps(self, mock_run):
        mocked_output_with_gps = """
        ExifTool Version Number         : 12.56
        File Name                       : test_MetaDetective-Franck_FERMAN-GPS.jpg
        Camera Model Name               : Pixel 2
        GPS Position                    : 47 deg 28' 0.86" N, 10 deg 12' 13.50" E
        Formatted GPS Position          : 47.466906, 10.203750
        Address                         : Hörner Höhenweg, Bolsterlang, Hörnergruppe (VGem), Landkreis Oberallgäu, Bayern, 87538, Deutschland
        Map Link                        : https://nominatim.openstreetmap.org/ui/reverse.html?lat=47.466906&lon=10.203750
        """

        mock_result = Mock()
        mock_result.stdout = mocked_output_with_gps
        mock_run.return_value = mock_result

        metadata = get_metadata("test_MetaDetective-Franck_FERMAN-GPS.jpg", ["File Name", "Camera Model Name", "Formatted GPS Position", "Address", "Map Link"])

        self.assertIn("File Name", metadata)
        self.assertEqual(metadata["File Name"], "test_MetaDetective-Franck_FERMAN-GPS.jpg")
        self.assertIn("Camera Model Name", metadata)
        self.assertEqual(metadata["Camera Model Name"], "Pixel 2")
        self.assertIn("Formatted GPS Position", metadata)
        self.assertEqual(metadata["Formatted GPS Position"], "47.466906, 10.203750")
        self.assertIn("Address", metadata)
        self.assertEqual(metadata["Address"], "Hörner Höhenweg, Bolsterlang, Hörnergruppe (VGem), Landkreis Oberallgäu, Bayern, 87538, Deutschland")
        self.assertIn("Map Link", metadata)
        self.assertEqual(metadata["Map Link"], "https://nominatim.openstreetmap.org/ui/reverse.html?lat=47.466906&lon=10.203750")

# Tests for matches_any_pattern
class TestMatchesAnyPattern(unittest.TestCase):

    def test_matches_pattern(self):
        patterns = ["hello", "world", "^test"]
        self.assertTrue(matches_any_pattern("hello world", patterns))
        self.assertTrue(matches_any_pattern("test123", patterns))
        self.assertFalse(matches_any_pattern("hi", patterns))

    def test_no_match_with_patterns(self):
        patterns = ["abc", "def", "^xyz"]
        self.assertFalse(matches_any_pattern("ghijkl", patterns))

    def test_case_insensitive_matching(self):
        patterns = ["hello", "world"]
        self.assertTrue(matches_any_pattern("HeLLo WoRLD", patterns))
        self.assertTrue(matches_any_pattern("HELLO", patterns))
        self.assertFalse(matches_any_pattern("bye", patterns))

    def test_empty_patterns(self):
        patterns = []
        self.assertFalse(matches_any_pattern("hello", patterns))

    def test_special_characters(self):
        patterns = ["^a.b$", "test.*123"]
        self.assertTrue(matches_any_pattern("aXb", patterns))
        self.assertTrue(matches_any_pattern("test---123", patterns))
        self.assertTrue(matches_any_pattern("axb", patterns))

# Tests for get_files
class TestGetFiles(unittest.TestCase):

    def setUp(self):
        self.sample_dir = "/tmp/sample_dir"
        os.makedirs(self.sample_dir, exist_ok=True)
        self.sample_files = ["file1.txt", "file2.jpg", "file3.docx"]
        for file in self.sample_files:
            open(os.path.join(self.sample_dir, file), 'a').close()

    def tearDown(self):
        shutil.rmtree(self.sample_dir)

    def test_directory_with_valid_files(self):
        args = Mock(directory=self.sample_dir, type=['all'], files=[])
        result_files = sorted(get_files(args))
        expected_files = sorted([
            os.path.join(self.sample_dir, "file1.txt"),
            os.path.join(self.sample_dir, "file2.jpg"),
            os.path.join(self.sample_dir, "file3.docx"),
        ])
        self.assertListEqual(result_files, expected_files)

    def test_directory_with_filtered_files(self):
        mock_args = Mock()
        mock_args.directory = self.sample_dir
        mock_args.type = ['.txt']
        mock_args.files = None
        result_files = get_files(mock_args)
        self.assertEqual(result_files, [os.path.join(self.sample_dir, "file1.txt")])

    def test_invalid_directory(self):
        mock_args = Mock()
        mock_args.directory = "/invalid/dir"
        mock_args.type = ['all']
        mock_args.files = None
        with self.assertRaises(SystemExit) as cm:
            get_files(mock_args)
        self.assertEqual(cm.exception.code, "Error: /invalid/dir is not a directory.")

    def test_files_argument(self):
        mock_args = Mock()
        mock_args.directory = None
        mock_args.type = ['all']
        mock_args.files = [os.path.join(self.sample_dir, file) for file in self.sample_files]
        result_files = get_files(mock_args)
        self.assertListEqual(result_files, mock_args.files)

    def test_no_files_found(self):
        mock_args = Mock()
        mock_args.directory = self.sample_dir
        mock_args.type = ['.doc']
        mock_args.files = None
        with self.assertRaises(SystemExit) as cm:
            get_files(mock_args)
        self.assertEqual(cm.exception.code, "Error: No files found.")

# Tests for get_address_from_coords
class TestGetAddressFromCoords(unittest.TestCase):

    @patch("http.client.HTTPSConnection")
    def test_successful_response(self, mock_conn):
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "display_name": "4 Chome-31-10 Jingumae, Shibuya City, Tokyo 150-0001, Japon"
        }).encode("utf-8")
        mock_conn.return_value.getresponse.return_value = mock_response
        
        address = get_address_from_coords("35.66930", "139.70607")
        
        self.assertEqual(address, "4 Chome-31-10 Jingumae, Shibuya City, Tokyo 150-0001, Japon")
        
    @patch("http.client.HTTPSConnection")
    def test_failed_response(self, mock_conn):
        mock_conn.return_value.request.side_effect = Exception("API Connection Error")
        
        address = get_address_from_coords("35.66930", "139.70607")
        
        self.assertEqual(address, "")

    @patch("http.client.HTTPSConnection")
    def test_unexpected_response(self, mock_conn):
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({}).encode("utf-8")
        mock_conn.return_value.getresponse.return_value = mock_response
        
        address = get_address_from_coords("35.66930", "139.70607")
        
        self.assertEqual(address, "")


if __name__ == '__main__':
    unittest.main()
