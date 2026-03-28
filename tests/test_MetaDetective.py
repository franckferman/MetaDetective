import argparse
import json
import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import Mock, patch

from src.MetaDetective import MetaDetective as md


# ============================================================================
# Banner et exiftool
# ============================================================================

class TestShowBanner(unittest.TestCase):
    def test_show_banner_prints_banner(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            md.show_banner()
            content = mock_stdout.getvalue()
            self.assertEqual(content, md.BANNER + "\n")


class TestCheckExiftoolInstalled(unittest.TestCase):

    @patch("src.MetaDetective.MetaDetective.subprocess.run")
    def test_exiftool_is_installed_no_exit(self, mock_run):
        mock_run.return_value = Mock()
        try:
            md.check_exiftool_installed()
        except SystemExit as e:
            self.fail(f"Unexpected SystemExit: {e}")

    @patch("src.MetaDetective.MetaDetective.subprocess.run")
    def test_exiftool_not_installed_raises_system_exit(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(SystemExit) as cm:
            md.check_exiftool_installed()
        self.assertEqual(str(cm.exception), md.EXIFTOOL_NOT_INSTALLED)

    @patch("src.MetaDetective.MetaDetective.subprocess.run")
    def test_exiftool_execution_error_raises_system_exit(self, mock_run):
        mock_run.side_effect = md.subprocess.CalledProcessError(
            returncode=1, cmd=["exiftool", "-ver"]
        )
        with self.assertRaises(SystemExit) as cm:
            md.check_exiftool_installed()
        self.assertEqual(str(cm.exception), md.EXIFTOOL_EXECUTION_ERROR)


# ============================================================================
# GPSProcessor: dms_to_dd / parse_dms
# ============================================================================

class TestGPSProcessorDmsToDd(unittest.TestCase):

    def test_north_positive(self):
        result = md.GPSProcessor.dms_to_dd(40, 26, 46, "N")
        self.assertAlmostEqual(result, 40.4461111, places=6)

    def test_south_negative(self):
        result = md.GPSProcessor.dms_to_dd(40, 26, 46, "S")
        self.assertAlmostEqual(result, -40.4461111, places=6)

    def test_east_positive(self):
        result = md.GPSProcessor.dms_to_dd(40, 26, 46, "E")
        self.assertAlmostEqual(result, 40.4461111, places=6)

    def test_west_negative(self):
        result = md.GPSProcessor.dms_to_dd(40, 26, 46, "W")
        self.assertAlmostEqual(result, -40.4461111, places=6)

    def test_invalid_degrees(self):
        with self.assertRaises(ValueError):
            md.GPSProcessor.dms_to_dd(200, 26, 46, "N")

    def test_invalid_minutes(self):
        with self.assertRaises(ValueError):
            md.GPSProcessor.dms_to_dd(40, 60, 46, "N")

    def test_invalid_seconds(self):
        with self.assertRaises(ValueError):
            md.GPSProcessor.dms_to_dd(40, 26, 60, "N")

    def test_invalid_direction(self):
        with self.assertRaises(ValueError):
            md.GPSProcessor.dms_to_dd(40, 26, 46, "A")

    def test_case_insensitive_direction(self):
        result = md.GPSProcessor.dms_to_dd(40, 26, 46, "n")
        self.assertAlmostEqual(result, 40.4461111, places=6)


class TestGPSProcessorParseDms(unittest.TestCase):

    def test_valid_dms_north(self):
        result = md.GPSProcessor.parse_dms('50 deg 49\' 8.59" N')
        self.assertEqual(result, (50, 49, 8.59, "N"))

    def test_valid_dms_east(self):
        result = md.GPSProcessor.parse_dms('50 deg 49\' 8.59" E')
        self.assertEqual(result, (50, 49, 8.59, "E"))

    def test_invalid_direction(self):
        with self.assertRaises(ValueError):
            md.GPSProcessor.parse_dms('50 deg 49\' 8.59" A')

    def test_missing_degrees(self):
        with self.assertRaises(ValueError):
            md.GPSProcessor.parse_dms('49\' 8.59" N')

    def test_missing_minutes(self):
        with self.assertRaises(ValueError):
            md.GPSProcessor.parse_dms('50 deg 8.59" N')

    def test_missing_seconds(self):
        with self.assertRaises(ValueError):
            md.GPSProcessor.parse_dms("50 deg 49' N")

    def test_case_insensitive_direction(self):
        result = md.GPSProcessor.parse_dms('50 deg 49\' 8.59" n')
        self.assertEqual(result, (50, 49, 8.59, "N"))


# ============================================================================
# MetadataExtractor + GPSProcessor.process_gps_data
# ============================================================================

class TestMetadataExtractor(unittest.TestCase):

    @patch("src.MetaDetective.MetaDetective.subprocess.run")
    def test_get_metadata_basic_fields(self, mock_run):
        mocked_output = """File Name                       : test.pdf
Author                          : Franck
Camera Model Name               : Pixel
"""
        mock_result = Mock()
        mock_result.stdout = mocked_output
        mock_run.return_value = mock_result

        metadata = md.MetadataExtractor.get_metadata(
            "test.pdf",
            ["File Name", "Author", "Camera Model Name"]
        )

        self.assertEqual(metadata["File Name"], "test.pdf")
        self.assertEqual(metadata["Author"], "Franck")
        self.assertEqual(metadata["Camera Model Name"], "Pixel")

    @patch("src.MetaDetective.MetaDetective.subprocess.run")
    def test_get_metadata_with_gps_position(self, mock_run):
        mocked_output = """GPS Position                    : 47 deg 28' 0.86" N, 10 deg 12' 13.50" E
File Name                       : gps.jpg
"""
        mock_result = Mock()
        mock_result.stdout = mocked_output
        mock_run.return_value = mock_result

        metadata = md.MetadataExtractor.get_metadata(
            "gps.jpg",
            ["File Name", "GPS Position", "Formatted GPS Position"]
        )

        self.assertIn("GPS Position", metadata)
        self.assertIn("Formatted GPS Position", metadata)
        lat, lon = metadata["Formatted GPS Position"].split(", ")
        float(lat)
        float(lon)

    @patch("src.MetaDetective.MetaDetective.subprocess.run")
    def test_get_metadata_handles_called_process_error(self, mock_run):
        mock_run.side_effect = md.subprocess.CalledProcessError(
            returncode=1, cmd=["exiftool", "badfile"]
        )
        metadata = md.MetadataExtractor.get_metadata("badfile", ["File Name"])
        self.assertEqual(metadata, {})


# ============================================================================
# AddressResolver
# ============================================================================

class TestAddressResolver(unittest.TestCase):

    @patch("src.MetaDetective.MetaDetective.http.client.HTTPSConnection")
    def test_get_address_from_coords_fetch_and_cache(self, mock_conn_cls):
        # Fake HTTP response
        conn_instance = Mock()
        mock_conn_cls.return_value = conn_instance

        response = Mock()
        response.read.return_value = json.dumps(
            {"display_name": "Somewhere, Earth"}
        ).encode("utf-8")
        conn_instance.getresponse.return_value = response

        # First call - should hit HTTP
        addr1 = md.AddressResolver.get_address_from_coords("47.0", "10.0")
        self.assertEqual(addr1, "Somewhere, Earth")
        self.assertTrue(mock_conn_cls.called)

        calls_count_after_first = mock_conn_cls.call_count

        # Second call same coords - should use cache, no new HTTPSConnection
        addr2 = md.AddressResolver.get_address_from_coords("47.0", "10.0")
        self.assertEqual(addr2, "Somewhere, Earth")
        self.assertEqual(mock_conn_cls.call_count, calls_count_after_first)

    @patch.object(md.AddressResolver, "get_address_from_coords", return_value="Somewhere, Earth")
    def test_format_gps_data_adds_address_and_map_link(self, mock_get_addr):
        metadata = {"Formatted GPS Position": "47.466906, 10.203750"}
        md.AddressResolver.format_gps_data(metadata)

        self.assertEqual(metadata["Address"], "Somewhere, Earth")
        self.assertIn("Map Link", metadata)
        self.assertIn("lat=47.466906", metadata["Map Link"])
        self.assertIn("lon=10.203750", metadata["Map Link"])
        mock_get_addr.assert_called_once()


# ============================================================================
# WebScraper.is_valid_file_link
# ============================================================================

class TestWebScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = md.WebScraper(["pdf", "jpg", "png"])

    def test_valid_file_link_pdf(self):
        self.assertTrue(
            self.scraper.is_valid_file_link("https://example.com/documents/report.pdf")
        )

    def test_valid_file_link_jpg_with_query(self):
        self.assertTrue(
            self.scraper.is_valid_file_link("https://example.com/img/photo.JPG?version=1")
        )

    def test_invalid_file_link_no_extension(self):
        self.assertFalse(
            self.scraper.is_valid_file_link("https://example.com/download")
        )

    def test_invalid_file_link_wrong_extension(self):
        self.assertFalse(
            self.scraper.is_valid_file_link("https://example.com/script.js")
        )


# ============================================================================
# FileDownloader utils (hash) - pas de HTTP
# ============================================================================

class TestFileDownloader(unittest.TestCase):

    def test_calculate_hash_is_deterministic(self):
        data = b"Hello world"
        h1 = md.FileDownloader.calculate_hash(data)
        h2 = md.FileDownloader.calculate_hash(data)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 8)  # CRC32 hex


# ============================================================================
# FileOperations + validation helpers
# ============================================================================

class TestFileOperations(unittest.TestCase):

    def test_filter_files_by_extension_basic(self):
        files = [
            "test1.pdf",
            "test2.docx",
            "image.jpg",
            "notes.txt",
            "archive.tar.gz",
        ]
        filtered = md.FileOperations.filter_files_by_extension(files, [".pdf", ".jpg"])
        self.assertIn("test1.pdf", filtered)
        self.assertIn("image.jpg", filtered)
        self.assertNotIn("test2.docx", filtered)
        self.assertNotIn("notes.txt", filtered)

    def test_filter_files_by_extension_type_errors(self):
        with self.assertRaises(TypeError):
            md.FileOperations.filter_files_by_extension("not_a_list", [".pdf"])
        with self.assertRaises(TypeError):
            md.FileOperations.filter_files_by_extension(["file.pdf"], "not_a_list")

    def test_get_files_from_directory_with_type_filter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "a.pdf")
            txt_path = os.path.join(tmpdir, "b.txt")
            with open(pdf_path, "w"):
                pass
            with open(txt_path, "w"):
                pass

            class Args:
                directory = tmpdir
                files = None
                type = [".pdf"]

            files = md.FileOperations.get_files(Args)
            self.assertEqual(files, [pdf_path])

    def test_get_files_from_args_files(self):
        class Args:
            directory = None
            files = ["a.pdf", "b.txt"]
            type = ["all"]

        files = md.FileOperations.get_files(Args)
        self.assertEqual(files, ["a.pdf", "b.txt"])

    def test_get_files_no_files_raises(self):
        class Args:
            directory = None
            files = []
            type = ["all"]

        with self.assertRaises(ValueError):
            md.FileOperations.get_files(Args)


class TestValidDirectory(unittest.TestCase):

    def test_valid_directory_ok(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(md.valid_directory(tmpdir), tmpdir)

    def test_invalid_directory_not_exists(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            md.valid_directory("/this/path/does/not/exist")

    def test_invalid_directory_not_a_dir(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            with self.assertRaises(argparse.ArgumentTypeError):
                md.valid_directory(tmpfile.name)


class TestValidFilename(unittest.TestCase):

    def test_valid_filename_basic(self):
        self.assertEqual(md.valid_filename("export01"), "export01")

    def test_valid_filename_with_dash_underscore(self):
        # 16 chars, termine par un alphanum, respecte MAX_FILENAME_LENGTH
        self.assertEqual(md.valid_filename("meta_detective_1"), "meta_detective_1")

    def test_invalid_filename_empty(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            md.valid_filename("")

    def test_invalid_filename_too_long(self):
        value = "a" * (md.MAX_FILENAME_LENGTH + 1)
        with self.assertRaises(argparse.ArgumentTypeError):
            md.valid_filename(value)

    def test_invalid_filename_ending_with_dash(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            md.valid_filename("export-")

    def test_invalid_filename_ending_with_underscore(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            md.valid_filename("export_")


class TestValidUrl(unittest.TestCase):

    def test_valid_http_url(self):
        url = "http://example.com/resource?id=1"
        self.assertEqual(md.valid_url(url), url)

    def test_valid_https_url(self):
        url = "https://example.com/res.pdf"
        self.assertEqual(md.valid_url(url), url)

    def test_invalid_url(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            md.valid_url("not_a_url")

        with self.assertRaises(argparse.ArgumentTypeError):
            md.valid_url("ftp://example.com/file")


# ============================================================================
# PatternMatcher.matches_any_pattern
# ============================================================================

class TestPatternMatcher(unittest.TestCase):

    def test_matches_any_pattern_true(self):
        value = "admin@example.com"
        patterns = [r"admin", r"root"]
        self.assertTrue(md.PatternMatcher.matches_any_pattern(value, patterns))

    def test_matches_any_pattern_false(self):
        value = "user@example.com"
        patterns = [r"admin", r"root"]
        self.assertFalse(md.PatternMatcher.matches_any_pattern(value, patterns))

    def test_matches_any_pattern_empty_list(self):
        self.assertFalse(md.PatternMatcher.matches_any_pattern("anything", []))


if __name__ == "__main__":
    unittest.main()
