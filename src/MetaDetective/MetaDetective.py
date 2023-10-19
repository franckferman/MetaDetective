#!/usr/bin/env python3

"""Unleash Metadata Intelligence with MetaDetective. Your Assistant Beyond Metagoofil.

Created By  : Franck FERMAN @franckferman
Created Date: 27/08/2023
Version     : 1.0.5 (19/10/2023)
"""

import argparse
import datetime
import http.client
import io
import json
import os
import re
import subprocess
import sys
from argparse import Namespace
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


BANNER = r"""
___  ___     _       ______     _            _   _
|  \/  |    | |      |  _  \   | |          | | (_)
| .  . | ___| |_ __ _| | | |___| |_ ___  ___| |_ ___   _____
| |\/| |/ _ \ __/ _` | | | / _ \ __/ _ \/ __| __| \ \ / / _ \
| |  | |  __/ || (_| | |/ /  __/ ||  __/ (__| |_| |\ V /  __/
\_|  |_/\___|\__\__,_|___/ \___|\__\___|\___|\__|_| \_/ \___|
"""
FIELDS = [
    "File Name", "Title", "Creator", "Author", "Last Modified By", "Create Date", "Modify Date",
    "Hyperlinks", "Company", "Creator Tool", "Producer", "Software", "Camera Model Name", "Image Description",
    "Make", "Camera ID", "Camera Type 2", "Serial Number", "Internal Serial Number", "GPS Status", "GPS Altitude",
    "GPS Latitude", "GPS Longitude", "GPS Position", "Formatted GPS Position", "Address", "Map Link"
]
UNIQUE_FIELDS = [
    "Creator", "Author", "Last Modified By", "Hyperlinks", "Creator Tool",
    "Producer", "Software", "Camera Model Name", "Image Description", "Make",
    "Camera ID", "GPS Position", "Formatted GPS Position", "Map Link"
]


def show_banner() -> None:
    """Print the banner."""
    print(BANNER)


def check_exiftool_installed() -> None:
    """Verify exiftool installation and exit the program if absent or on execution error."""
    EXIFTOOL_NOT_INSTALLED = "Error: exiftool is not installed. Please install it to continue."
    EXIFTOOL_EXECUTION_ERROR = "Error: exiftool encountered an error."

    try:
        subprocess.run(["exiftool", "-ver"], capture_output=True, check=True, text=True)
    except FileNotFoundError:
        sys.exit(EXIFTOOL_NOT_INSTALLED)
    except subprocess.CalledProcessError:
        sys.exit(EXIFTOOL_EXECUTION_ERROR)


def dms_to_dd(degrees: int, minutes: int, seconds: float, direction: str) -> float:
    """
    Convert coordinates from DMS (Degree-Minute-Second) to DD (Decimal Degrees).

    Args:
        degrees (int): Degrees component of DMS.
        minutes (int): Minutes component of DMS.
        seconds (float): Seconds component of DMS.
        direction (str): Hemisphere identifier ('N', 'S', 'E', 'W').
        'N' and 'E' yield positive values; 'S' and 'W' yield negative values.

    Returns:
        float: Coordinate in Decimal Degrees format.
    """
    dd = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    if direction in ['S', 'W']:
        dd *= -1
    return dd


def parse_dms(dms_str: str) -> Optional[Tuple[int, int, float, str]]:
    """
    Parse a DMS (Degree-Minute-Second) string into its components.

    Args:
        dms_str (str): String in DMS format, e.g., "50 deg 49' 8.59\" N".

    Returns:
        Optional[Tuple[int, int, float, str]]:
        Components (degrees, minutes, seconds, direction)
        of the DMS if parsed successfully, otherwise None.
    """
    match = re.search(r"(\d+) deg (\d+)' ([\d.]+)\" (\w)", dms_str)
    if match:
        deg, min, sec, dir = match.groups()
        return int(deg), int(min), float(sec), dir
    return None


def get_metadata(file_path: str, fields: List[str]) -> dict:
    """
    Retrieve specified metadata fields from a file using exiftool.

    Args:
        file_path (str): Path of the file to analyze.
        fields (List[str]): List of metadata fields to extract.

    Returns:
        dict: Dictionary containing the extracted metadata.
    """
    exiftool_output = subprocess.run(["exiftool", file_path], capture_output=True, text=True)
    metadata = {}

    for line in exiftool_output.stdout.splitlines():
        for field in fields:
            if field in line:
                key, value = line.split(":", 1)
                if value.strip():
                    metadata[key.strip()] = value.strip()

    gps_position = metadata.get("GPS Position", None)
    if gps_position:
        lat_str, lon_str = gps_position.split(", ")
        lat_dd = dms_to_dd(*parse_dms(lat_str))
        lon_dd = dms_to_dd(*parse_dms(lon_str))
    else:
        gps_lat = metadata.get("GPS Latitude", None)
        gps_lon = metadata.get("GPS Longitude", None)
        if gps_lat and gps_lon:
            lat_dd = dms_to_dd(*parse_dms(gps_lat))
            lon_dd = dms_to_dd(*parse_dms(gps_lon))
        else:
            lat_dd, lon_dd = None, None

    if lat_dd is not None and lon_dd is not None:
        metadata["Formatted GPS Position"] = f"{lat_dd:.6f}, {lon_dd:.6f}"

    return metadata


def matches_any_pattern(value: str, patterns: List[str]) -> bool:
    """
    Check if a string matches any of the provided patterns.

    Args:
        value (str): The string to check.
        patterns (List[str]): List of patterns to check against.

    Returns:
        bool: True if the value matches any of the patterns, False otherwise.
    """
    return any(re.search(pattern, value, re.IGNORECASE) for pattern in patterns)


def get_files(args) -> List[str]:
    """
    Retrieve a list of files based on the provided arguments.

    Args:
        args: The parsed command-line arguments.

    Returns:
        List[str]: List of file paths.
    """
    if args.directory:
        if not os.path.isdir(args.directory):
            sys.exit(f"Error: {args.directory} is not a directory.")

        files = [os.path.join(args.directory, file) for file in os.listdir(args.directory)]
        if args.type != ['all']:
            files = [file for file in files if any(file.endswith(ext) for ext in args.type)]
    else:
        files = args.files

    if not files:
        sys.exit("Error: No files found.")
    return files


def get_address_from_coords(lat: str, lon: str) -> str:
    """
    Fetch address from latitude and longitude using the Nominatim API.

    Args:
        lat (str): Latitude as a string.
        lon (str): Longitude as a string.

    Returns:
        str: Address as a string. Returns an empty string if there's an error or nothing found.
    """
    try:
        conn = http.client.HTTPSConnection("nominatim.openstreetmap.org")
        headers = {'User-Agent': 'MetaDetective/1.0.5'}
        conn.request("GET", f"/reverse?format=jsonv2&lat={lat}&lon={lon}", headers=headers)

        res = conn.getresponse()
        data = res.read()

        parsed_data = json.loads(data.decode("utf-8"))
        address = parsed_data.get("display_name", "")

        return address

    except Exception:
        return ""


def display_metadata(args: Namespace, all_metadata: List[Dict[str, str]], ignore_patterns: List[str]) -> None:
    """
    Display metadata based on the provided arguments.

    Args:
        args (Namespace): The parsed command-line arguments.
        all_metadata (List[Dict[str, str]]): List of dictionaries containing metadata.
        ignore_patterns (List[str]): List of patterns to ignore.

    Returns:
        None
    """
    if args.display == "all":
        for metadata in all_metadata:
            formatted_gps = metadata.get("Formatted GPS Position")
            if formatted_gps:
                lat, lon = formatted_gps.split(", ")
                address = get_address_from_coords(lat, lon)
                if address:
                    metadata["Address"] = address
                metadata["Map Link"] = f"https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat}&lon={lon}"

            displayed_fields = 0

            for field, value in metadata.items():
                if field in FIELDS and value and not matches_any_pattern(value, ignore_patterns):
                    print(f"{field}: {value}")
                    displayed_fields += 1
            if displayed_fields == 1:
                print("No relevant metadata found.")
            print("-" * 40)

    elif args.display == "singular":
        unique_values = defaultdict(set)

        for metadata in all_metadata:
            formatted_gps = metadata.get("Formatted GPS Position")
            if formatted_gps:
                lat, lon = formatted_gps.split(", ")
                map_link = f"https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat}&lon={lon}"
                if map_link:
                    metadata["Map Link"] = map_link

            for field in UNIQUE_FIELDS:
                value = metadata.get(field, None)
                if field == "Hyperlinks" and value:
                    links = [link.strip() for link in value.split(',')]
                    valid_links = [link for link in links if not matches_any_pattern(link, ignore_patterns)]
                    if valid_links:
                        unique_values[field].add(', '.join(valid_links))
                elif value and not matches_any_pattern(value, ignore_patterns):
                    unique_values[field].add(value)

        for field, values in unique_values.items():
            unique_cased_values = {next(v for v in values if v.lower() == value.lower()): None for value in values}.keys()
            if unique_cased_values:
                if args.format == 'formatted':
                    print(f"{field}:")
                    for unique_value in unique_cased_values:
                        print(f"    - {unique_value}")
                else:
                    print(f"{field}: {', '.join(unique_cased_values)}")
                print()


def export_metadata_to_html(args: Namespace, all_metadata: List[Dict[str, str]], ignore_patterns: List[str]) -> str:
    """
    Convert metadata to HTML format based on the provided arguments.

    Args:
        args (Namespace): The parsed command-line arguments.
        all_metadata (List[Dict[str, str]]): List of dictionaries containing metadata.
        ignore_patterns (List[str]): List of patterns to ignore.

    Returns:
        str: HTML representation of the metadata.
    """
    html_parts = ['''<html>
<head>
    <title>MetaDetective Export</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #EAEAEA;
            padding: 20px;
            margin: 0;
        }
        .header {
            background-color: #333;
            color: white;
            padding: 10px 0;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .metadata-entry {
            background-color: #1E1E1E;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
        }
        p {
            margin: 5px 0;
        }
        strong {
            color: #EAEAEA;
        }
        h3 {
            color: #BBB;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }
        hr {
            border: 0;
            border-top: 1px solid #333;
            margin-top: 10px;
        }
        a:link {
            color: #BBB;
            text-decoration: none;
            transition: color 0.3s;
        }
        a:visited {
            color: #888;
            text-decoration: none;
        }
        a:hover {
            color: #FFF;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>MetaDetective Export Report</h1>
    </div>
''']

    if args.display == "all":
        for metadata in all_metadata:
            html_parts.append('<div class="metadata-entry">')

            formatted_gps = metadata.get("Formatted GPS Position")
            if formatted_gps:
                lat, lon = formatted_gps.split(", ")
                address = get_address_from_coords(lat, lon)
                if address:
                    metadata["Address"] = address
                metadata["Map Link"] = f"<a href='https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat}&lon={lon}'>View on Map</a>"

            displayed_fields = 0
            for field, value in metadata.items():
                if field in FIELDS and value and not matches_any_pattern(value, ignore_patterns):
                    html_parts.append(f'<p><strong>{field}:</strong> {value}</p>')
                    displayed_fields += 1

            if displayed_fields == 1:
                html_parts.append('<p>No relevant metadata found.</p>')

            html_parts.append('<hr></div>')
    elif args.display == "singular":
        unique_values = defaultdict(set)

        for metadata in all_metadata:
            formatted_gps = metadata.get("Formatted GPS Position")
            if formatted_gps:
                lat, lon = formatted_gps.split(", ")
                map_link = f"https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat}&lon={lon}"
                metadata["Map Link"] = f"<a href='{map_link}'>View on Map</a>"

            for field in UNIQUE_FIELDS:
                value = metadata.get(field, None)
                if field == "Hyperlinks" and value:
                    links = [link.strip() for link in value.split(',')]
                    valid_links = [link for link in links if not matches_any_pattern(link, ignore_patterns)]
                    if valid_links:
                        unique_values[field].add(', '.join(valid_links))
                elif value and not matches_any_pattern(value, ignore_patterns):
                    unique_values[field].add(value)

        for field, values in unique_values.items():
            unique_cased_values = {next(v for v in values if v.lower() == value.lower()): None for value in values}.keys()
            if unique_cased_values:
                html_parts.append(f'<h3>{field}:</h3>')
                if args.format == 'formatted':
                    for unique_value in unique_cased_values:
                        html_parts.append(f'<p>    - {unique_value}</p>')
                else:
                    html_parts.append(f"<p>{', '.join(unique_cased_values)}</p>")
                html_parts.append('<hr>')

    html_parts.append('</body></html>')
    return ''.join(html_parts)


def export_metadata_to_txt(args: Namespace, all_metadata: List[Dict[str, str]], ignore_patterns: List[str]) -> str:
    """
    Convert metadata to a text string based on the provided arguments.

    Args:
        args (Namespace): The parsed command-line arguments.
        all_metadata (List[Dict[str, str]]): List of dictionaries containing metadata.
        ignore_patterns (List[str]): List of patterns to ignore.

    Returns:
        str: The formatted metadata as a string.
    """
    output = io.StringIO()

    def print_to_buffer(*args, **kwargs):
        print(*args, file=output, **kwargs)

    if args.display == "all":
        for metadata in all_metadata:
            formatted_gps = metadata.get("Formatted GPS Position")
            if formatted_gps:
                lat, lon = formatted_gps.split(", ")
                address = get_address_from_coords(lat, lon)
                if address:
                    metadata["Address"] = address
                metadata["Map Link"] = f"https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat}&lon={lon}"

            displayed_fields = 0

            for field, value in metadata.items():
                if field in FIELDS and value and not matches_any_pattern(value, ignore_patterns):
                    print_to_buffer(f"{field}: {value}")
                    displayed_fields += 1
            if displayed_fields == 1:
                print_to_buffer("No relevant metadata found.")
            print_to_buffer("-" * 40)

    elif args.display == "singular":
        unique_values = defaultdict(set)

        for metadata in all_metadata:
            formatted_gps = metadata.get("Formatted GPS Position")
            if formatted_gps:
                lat, lon = formatted_gps.split(", ")
                map_link = f"https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat}&lon={lon}"
                if map_link:
                    metadata["Map Link"] = map_link

            for field in UNIQUE_FIELDS:
                value = metadata.get(field, None)
                if field == "Hyperlinks" and value:
                    links = [link.strip() for link in value.split(',')]
                    valid_links = [link for link in links if not matches_any_pattern(link, ignore_patterns)]
                    if valid_links:
                        unique_values[field].add(', '.join(valid_links))
                elif value and not matches_any_pattern(value, ignore_patterns):
                    unique_values[field].add(value)

        for field, values in unique_values.items():
            unique_cased_values = {next(v for v in values if v.lower() == value.lower()): None for value in values}.keys()
            if unique_cased_values:
                if args.format == 'formatted':
                    print_to_buffer(f"{field}:")
                    for unique_value in unique_cased_values:
                        print_to_buffer(f"    - {unique_value}")
                else:
                    print_to_buffer(f"{field}: {', '.join(unique_cased_values)}")
                print_to_buffer()

    return output.getvalue()


def valid_filename(value):
    """Validate filename suffix.

    Check if the given filename suffix is valid. The filename should be:
    - Alphanumeric (both uppercase and lowercase allowed).
    - Less than 16 characters.
    - Can contain symbols '-' or '_', but not at the end.

    Parameters:
    - value (str): The filename suffix to validate.

    Returns:
    - str: The valid filename suffix.

    Raises:
    - argparse.ArgumentTypeError: If the filename suffix is invalid.
    """
    if not value:
        raise argparse.ArgumentTypeError("Filename suffix is empty.")

    if len(value) > 16:
        raise argparse.ArgumentTypeError("Filename suffix is longer than 16 characters.")

    if not value[-1].isalnum():
        raise argparse.ArgumentTypeError("Filename suffix ends with an invalid character.")

    for char in value:
        if not char.isalnum() and char not in ['-', '_']:
            raise argparse.ArgumentTypeError(f"Invalid character '{char}' in filename suffix.")

    return value


def valid_directory(path):
    """Validate directory path.

    Check if the given path is a valid directory.

    Parameters:
    - path (str): The directory path to validate.

    Returns:
    - str: The valid directory path.

    Raises:
    - argparse.ArgumentTypeError: If the directory path is invalid or doesn't exist.
    """
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Directory path '{path}' does not exist.")

    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"Path '{path}' is not a directory.")

    return path


def main():
    show_banner()
    check_exiftool_installed()

    parser = argparse.ArgumentParser(description="Retrieve and display metadata from files using exiftool.",
                                     epilog="Example commands:\n"
                                            "  python3 MetaDetective.py -d directory\n"
                                            "  python3 MetaDetective.py -d directory -i ^admin anonymous -t doc pdf\n"
                                            "  python3 MetaDetective.py -d directory -t all -display singular -format formatted\n"
                                            "  python3 MetaDetective.py -d directory --export\n",
                                     formatter_class=argparse.RawTextHelpFormatter
                                     )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--directory', help="Directory to analyze.")
    group.add_argument('-f', '--files', nargs='+', help="File or list of files to analyze.")
    parser.add_argument('-t', '--type', nargs='+', default=['all'], help="File extension(s) or 'all' for all files.")

    display_group = parser.add_argument_group('display options', 'Options affecting how metadata is displayed')
    display_group.add_argument('-i', '--ignore', nargs='+', help="Ignore specific items in display using regex or words.")
    display_group.add_argument('-display', choices=['all', 'singular'], default='singular', help="Display mode: 'all' or 'singular'")
    display_group.add_argument('-format', choices=['formatted', 'concise'], help="Display format for 'singular' mode: 'formatted' or 'concise'")

    export_group = parser.add_argument_group('export options', 'Options for exporting metadata')
    export_group.add_argument('-e', '--export', nargs='?', const='html', choices=['html', 'txt'], default=None, help="Export results. Optional formats: 'html' or 'txt'. If not specified, 'html' is the default.")
    export_group.add_argument('-c', '--custom', type=valid_filename, help="Add a custom suffix to the export filename. It should be alphanumeric and less than 16 characters.")
    export_group.add_argument('-o', '--output', type=valid_directory, default=os.getcwd(), help="Specify a custom output directory for the exported file.")

    args = parser.parse_args()

    ignore_patterns = args.ignore if args.ignore else []

    if args.display == 'all' and args.format:
        print("Error: The -format argument is not allowed with -display all.")
        sys.exit(1)

    if args.display == 'singular' and args.format is None:
        args.format = 'concise'

    files = get_files(args)

    all_metadata = [get_metadata(file, FIELDS) for file in files]

    if args.export:
        if args.export == 'html':
            content = export_metadata_to_html(args, all_metadata, ignore_patterns)
            file_extension = '.html'
        else:
            content = export_metadata_to_txt(args, all_metadata, ignore_patterns)
            file_extension = '.txt'

        timestamp = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
        custom_suffix = f"{args.custom}-" if args.custom else ""
        filename = f"MetaDetective_Export-{custom_suffix}{timestamp}{file_extension}"

        full_path = os.path.join(args.output, filename)

        with open(full_path, "w") as f:
            f.write(content)
        print(f"Metadata exported to {filename}")
    else:
        display_metadata(args, all_metadata, ignore_patterns)


if __name__ == "__main__":
    main()
