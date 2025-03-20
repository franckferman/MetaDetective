import argparse
import http.client
import json
import os
import re
import subprocess
import tempfile
import unittest
from io import StringIO
from unittest.mock import Mock, patch

from src.MetaDetective.MetaDetective import (BANNER, show_banner, check_exiftool_installed,
                                             dms_to_dd, parse_dms, get_metadata, matches_any_pattern,
                                             valid_directory, filter_files_by_extension, get_files,
                                             get_address_from_coords, format_gps_data, valid_filename,
                                             is_valid_file_link, valid_url)


class TestShowBanner(unittest.TestCase):
    def test_show_banner(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            show_banner()
            content = mock_stdout.getvalue()
            self.assertEqual(content, BANNER + "\n")


class TestExifToolCheck(unittest.TestCase):

    @patch('subprocess.run')
    def test_exiftool_is_installed(self, mock_run):
        """Test that the function doesn't raise an error when exiftool is installed."""
        mock_run.return_value = None
        try:
            check_exiftool_installed()
        except SystemExit as e:
            self.fail(f"Unexpected exit: {e}")

    @patch('subprocess.run')
    def test_raises_error_when_exiftool_not_installed(self, mock_run):
        """Test that the function raises an error when exiftool is not installed."""
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaisesRegex(SystemExit, "Error: exiftool is not installed. Please install it to continue."):
            check_exiftool_installed()

    @patch('subprocess.run')
    def test_raises_error_on_exiftool_execution_error(self, mock_run):
        """Test that the function raises an error when exiftool encounters an execution error."""
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=['exiftool', '-ver'])
        with self.assertRaisesRegex(SystemExit, "Error: exiftool encountered an error."):
            check_exiftool_installed()


class TestDMStoDD(unittest.TestCase):

    def test_dms_to_dd_north_positive(self):
        result = dms_to_dd(40, 26, 46, 'N')
        self.assertAlmostEqual(result, 40.4461111)

    def test_dms_to_dd_south_negative(self):
        result = dms_to_dd(40, 26, 46, 'S')
        self.assertAlmostEqual(result, -40.4461111)

    def test_dms_to_dd_east_positive(self):
        result = dms_to_dd(40, 26, 46, 'E')
        self.assertAlmostEqual(result, 40.4461111)

    def test_dms_to_dd_west_negative(self):
        result = dms_to_dd(40, 26, 46, 'W')
        self.assertAlmostEqual(result, -40.4461111)

    def test_invalid_degrees(self):
        with self.assertRaises(ValueError):
            dms_to_dd(200, 26, 46, 'N')

    def test_invalid_minutes(self):
        with self.assertRaises(ValueError):
            dms_to_dd(40, 60, 46, 'N')

    def test_invalid_seconds(self):
        with self.assertRaises(ValueError):
            dms_to_dd(40, 26, 60, 'N')

    def test_invalid_direction(self):
        with self.assertRaises(ValueError):
            dms_to_dd(40, 26, 46, 'A')

    def test_case_insensitive_direction(self):
        result = dms_to_dd(40, 26, 46, 'n')
        self.assertAlmostEqual(result, 40.4461111)


class TestParseDMS(unittest.TestCase):

    def test_valid_dms_north(self):
        result = parse_dms("50 deg 49' 8.59\" N")
        self.assertEqual(result, (50, 49, 8.59, 'N'))

    def test_valid_dms_east(self):
        result = parse_dms("50 deg 49' 8.59\" E")
        self.assertEqual(result, (50, 49, 8.59, 'E'))

    def test_invalid_direction(self):
        with self.assertRaises(ValueError):
            parse_dms("50 deg 49' 8.59\" A")

    def test_missing_degrees(self):
        with self.assertRaises(ValueError):
            parse_dms("49' 8.59\" N")

    def test_missing_minutes(self):
        with self.assertRaises(ValueError):
            parse_dms("50 deg 8.59\" N")

    def test_missing_seconds(self):
        with self.assertRaises(ValueError):
            parse_dms("50 deg 49' N")

    def test_case_insensitive_direction(self):
        result = parse_dms("50 deg 49' 8.59\" n")
        self.assertEqual(result, (50, 49, 8.59, 'N'))


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

    @patch("subprocess.run")
    def test_exiftool_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["exiftool", "file_path"])
        metadata = get_metadata("file_path", ["Field"])
        self.assertEqual(metadata, {})

    @patch("subprocess.run")
    def test_non_existent_fields(self, mock_run):
        mock_result = Mock()
        mock_result.stdout = self.mocked_exiftool_output
        mock_run.return_value = mock_result

        metadata = get_metadata("test_MetaDetective-Franck_FERMAN.pdf", ["File Name", "NonExistentField"])

        self.assertIn("File Name", metadata)
        self.assertNotIn("NonExistentField", metadata)


class TestMatchesAnyPattern(unittest.TestCase):

    def test_matches_pattern(self):
        value = "Hello, world!"
        patterns = ["^Hello, world!$", "Hello", "world"]
        self.assertTrue(matches_any_pattern(value, patterns))

    def test_does_not_match_pattern(self):
        value = "Hello, world!"
        patterns = ["^Hello$", "^world!$", "foo"]
        self.assertFalse(matches_any_pattern(value, patterns))

    def test_case_insensitive_matching(self):
        value = "Hello, WORLD!"
        patterns = ["^hello, world!$", "HELLO", "WORLD"]
        self.assertTrue(matches_any_pattern(value, patterns))

    def test_invalid_pattern(self):
        value = "Hello, world!"
        patterns = ["Hello[", "world"]
        with self.assertRaises(re.error):
            matches_any_pattern(value, patterns)

    def test_empty_string(self):
        value = ""
        patterns = ["^Hello, world!$", "Hello", "world"]
        self.assertFalse(matches_any_pattern(value, patterns))

    def test_empty_patterns(self):
        value = "Hello, world!"
        patterns = []
        self.assertFalse(matches_any_pattern(value, patterns))

    def test_matches_empty_pattern(self):
        value = "Hello, world!"
        patterns = ["^Hello, world!$", "", "world"]
        self.assertTrue(matches_any_pattern(value, patterns))


class TestValidDirectory(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()

    def tearDown(self):
        os.remove(self.temp_file.name)
        os.rmdir(self.temp_dir)

    def test_valid_directory(self):
        path = valid_directory(self.temp_dir)
        self.assertEqual(path, self.temp_dir)

    def test_invalid_directory_not_exist(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            valid_directory("/path/that/doesnt/exist")

    def test_invalid_directory_is_file(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            valid_directory(self.temp_file.name)

    def test_empty_directory_path(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            valid_directory("")


class TestFilterFilesByExtension(unittest.TestCase):

    def test_filter_files(self):
        files = ["test.txt", "example.jpg", "another.png", "sample.doc", "more.docx"]
        extensions = [".jpg", ".png"]
        filtered = filter_files_by_extension(files, extensions)
        self.assertEqual(filtered, ["example.jpg", "another.png"])

    def test_invalid_files_argument(self):
        with self.assertRaises(TypeError):
            filter_files_by_extension("string_instead_of_list", [".jpg"])

    def test_invalid_files_element(self):
        with self.assertRaises(TypeError):
            filter_files_by_extension([123, "example.jpg"], [".jpg"])

    def test_invalid_extensions_argument(self):
        with self.assertRaises(TypeError):
            filter_files_by_extension(["example.jpg"], "string_instead_of_list")

    def test_invalid_extensions_element(self):
        with self.assertRaises(TypeError):
            filter_files_by_extension(["example.jpg"], [".jpg", 123])

    def test_empty_files_list(self):
        extensions = [".jpg", ".png"]
        filtered = filter_files_by_extension([], extensions)
        self.assertEqual(filtered, [])

    def test_no_matching_files(self):
        files = ["test.txt", "sample.doc", "more.docx"]
        extensions = [".jpg", ".png"]
        filtered = filter_files_by_extension(files, extensions)
        self.assertEqual(filtered, [])


class TestGetFiles(unittest.TestCase):

    def setUp(self):
        self.mock_args_with_directory = Mock()
        self.mock_args_with_directory.directory = "/mock/directory"
        self.mock_args_with_directory.type = ["all"]
        self.mock_args_with_directory.files = []

        self.mock_args_with_files = Mock()
        self.mock_args_with_files.directory = None
        self.mock_args_with_files.type = ["all"]
        self.mock_args_with_files.files = ["/path/to/file1.txt", "/path/to/file2.jpg"]

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("os.listdir", return_value=["file1.txt", "file2.jpg"])
    def test_get_files_from_directory(self, mock_listdir, mock_isdir, mock_exists):
        files = get_files(self.mock_args_with_directory)
        self.assertEqual(files, ["/mock/directory/file1.txt", "/mock/directory/file2.jpg"])

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("os.listdir", return_value=["file1.txt", "file2.jpg"])
    def test_get_files_from_directory_with_filter(self, mock_listdir, mock_isdir, mock_exists):
        self.mock_args_with_directory.type = [".txt"]
        files = get_files(self.mock_args_with_directory)
        self.assertEqual(files, ["/mock/directory/file1.txt"])

    def test_get_files_from_args(self):
        files = get_files(self.mock_args_with_files)
        self.assertEqual(files, ["/path/to/file1.txt", "/path/to/file2.jpg"])

    @patch("os.path.isdir", return_value=False)
    def test_invalid_directory(self, mock_isdir):
        with self.assertRaises(ValueError):
            get_files(self.mock_args_with_directory)

    @patch("os.path.isdir", return_value=True)
    @patch("os.listdir", return_value=[])
    def test_no_files_in_directory(self, mock_listdir, mock_isdir):
        with self.assertRaises(ValueError):
            get_files(self.mock_args_with_directory)

    def test_no_files_in_args(self):
        self.mock_args_with_files.files = []
        with self.assertRaises(ValueError):
            get_files(self.mock_args_with_files)

    @patch("http.client.HTTPSConnection")
    def test_valid_response(self, MockHTTPSConnection):
        mock_response = Mock()
        mock_response.read.return_value = '{"display_name": "Berlin, Germany"}'.encode("utf-8")
        MockHTTPSConnection().getresponse.return_value = mock_response

        address = get_address_from_coords("52.5200", "13.4050")
        self.assertEqual(address, "Berlin, Germany")

    @patch("http.client.HTTPSConnection")
    def test_invalid_json(self, MockHTTPSConnection):
        mock_response = Mock()
        mock_response.read.return_value = 'Invalid JSON'.encode("utf-8")
        MockHTTPSConnection().getresponse.return_value = mock_response

        with self.assertRaisesRegex(json.JSONDecodeError, 'Expecting value'):
            get_address_from_coords("52.5200", "13.4050")

    @patch("http.client.HTTPSConnection")
    def test_http_error(self, MockHTTPSConnection):
        MockHTTPSConnection().request.side_effect = http.client.HTTPException("HTTP error")

        with self.assertRaises(http.client.HTTPException):
            get_address_from_coords("52.5200", "13.4050")

    @patch("http.client.HTTPSConnection")
    def test_no_display_name(self, MockHTTPSConnection):
        mock_response = Mock()
        mock_response.read.return_value = '{"name": "Berlin"}'.encode("utf-8")
        MockHTTPSConnection().getresponse.return_value = mock_response

        address = get_address_from_coords("52.5200", "13.4050")
        self.assertEqual(address, "")


class TestFormatGPSData(unittest.TestCase):

    def test_valid_formatted_gps_data_with_address(self):
        metadata = {"Formatted GPS Position": "52.5200, 13.4050"}

        format_gps_data(metadata)

        self.assertIn("Address", metadata)
        self.assertIn("Map Link", metadata)
        self.assertIn("52.5200", metadata["Map Link"])
        self.assertIn("13.4050", metadata["Map Link"])

    def test_no_formatted_gps_data(self):
        metadata = {"Some Other Data": "12345"}

        format_gps_data(metadata)

        self.assertNotIn("Address", metadata)
        self.assertNotIn("Map Link", metadata)

    def test_invalid_formatted_gps_data(self):
        metadata = {"Formatted GPS Position": "52.5200; 13.4050"}

        with self.assertRaises(ValueError):
            format_gps_data(metadata)


class TestValidFilename(unittest.TestCase):

    def test_valid_filename(self):
        """Test a valid filename."""
        filename = "example_123"
        self.assertEqual(valid_filename(filename), filename)

    def test_empty_filename(self):
        """Test an empty filename."""
        with self.assertRaises(argparse.ArgumentTypeError):
            valid_filename("")

    def test_long_filename(self):
        """Test a filename longer than 16 characters."""
        with self.assertRaises(argparse.ArgumentTypeError):
            valid_filename("a" * 17)

    def test_filename_ending_with_dash(self):
        """Test a filename ending with '-'."""
        with self.assertRaises(argparse.ArgumentTypeError):
            valid_filename("example-")

    def test_filename_ending_with_underscore(self):
        """Test a filename ending with '_'."""
        with self.assertRaises(argparse.ArgumentTypeError):
            valid_filename("example_")

    def test_filename_with_invalid_characters(self):
        """Test a filename with other invalid characters."""
        with self.assertRaises(argparse.ArgumentTypeError):
            valid_filename("example@123")


class TestIsValidFileLink(unittest.TestCase):

    def test_valid_file_link(self):
        """Test a valid file link."""
        link = "http://example.com/file.jpg"
        self.assertTrue(is_valid_file_link(link))

    def test_invalid_extension(self):
        """Test a link with no valid file extension."""
        link = "http://example.com/file.txt"
        self.assertFalse(is_valid_file_link(link))

    def test_extension_not_at_end(self):
        """Test a link where the extension is not at the end."""
        link = "http://example.com/file.jpg?query=123"
        self.assertTrue(is_valid_file_link(link))

    def test_no_path_in_link(self):
        """Test a link without any path."""
        link = "http://example.com"
        self.assertFalse(is_valid_file_link(link))

    def test_empty_link(self):
        """Test an empty link."""
        link = ""
        self.assertFalse(is_valid_file_link(link))


class TestValidUrl(unittest.TestCase):

    def test_valid_http_url(self):
        """Test a valid HTTP URL."""
        url = "http://example.com"
        self.assertEqual(valid_url(url), url)

    def test_valid_https_url(self):
        """Test a valid HTTPS URL."""
        url = "https://secure.example.com"
        self.assertEqual(valid_url(url), url)

    def test_invalid_url_no_protocol(self):
        """Test an invalid URL that lacks a protocol."""
        url = "example.com"
        with self.assertRaises(argparse.ArgumentTypeError):
            valid_url(url)

    def test_empty_url(self):
        """Test an empty URL."""
        url = ""
        with self.assertRaises(argparse.ArgumentTypeError):
            valid_url(url)


if __name__ == '__main__':
    unittest.main()
