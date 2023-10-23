#!/usr/bin/env python3

"""Unleash Metadata Intelligence with MetaDetective. Your Assistant Beyond Metagoofil.

Created By  : Franck FERMAN @franckferman
Created Date: 27/08/2023
Version     : 1.0.6 (23/10/2023)
"""

import argparse
import datetime
import http.client
import io
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
import urllib.request
from argparse import Namespace
from collections import defaultdict
from html.parser import HTMLParser
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin


BANNER = r"""
___  ___     _       ______     _            _   _     	 	 _==\/==_
|  \/  |    | |      |  _  \   | |          | | (_)    		/________\
| .  . | ___| |_ __ _| | | |___| |_ ___  ___| |_ ___   _____	/ 0 \ o b
| |\/| |/ _ \ __/ _` | | | / _ \ __/ _ \/ __| __| \ \ / / _ \	\___/'  |
| |  | |  __/ || (_| | |/ /  __/ ||  __/ (__| |_| |\ V /  __/	  H\__/'
\_|  |_/\___|\__\__,_|___/ \___|\__\___|\___|\__|_| \_/ \___|	  H
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

EXTENSIONS = [
    "csv", "xml",
    "email", "eml", "emlx", "msg", "oft", "ost", "pst", "vcf",
    "ai", "bmp", "gif", "ico", "jpeg", "jpg", "png", "ps", "psd", "svg", "tif", "tiff", "wepb",
    "key", "odp", "pps", "ppt", "pptx",
    "odf", "xls", "xlsm", "xlsx",
    "ico", "mp4", "mov",
    "doc", "docx", "odt", "pdf", "rtf", "tex", "wpd"
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
        headers = {'User-Agent': 'MetaDetective/1.0.6'}
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


def valid_filename(value: str) -> str:
    """
    Check if the filename is alphanumeric, less than 16 characters, and can contain symbols '-' or '_', but not at the end.

    Args:
        value (str): The filename suffix to validate.

    Returns:
        str: The valid filename suffix.

    Raises:
        argparse.ArgumentTypeError: If the filename suffix is invalid.
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


def valid_directory(path: str) -> str:
    """
    Validate directory path.

    Args:
        path (str): The directory path to validate.

    Returns:
        str: The valid directory path.

    Raises:
        argparse.ArgumentTypeError: If the directory path is invalid or doesn't exist.
    """
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Directory path '{path}' does not exist.")

    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"Path '{path}' is not a directory.")

    return path


class LinkParser(HTMLParser):
    """HTML Parser to extract links from a web page."""

    def __init__(self) -> None:
        """Initialize the LinkParser."""
        super().__init__()
        self.links: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        """Handle the start tag of an HTML element.

        Args:
            tag (str): The tag name of the HTML element.
            attrs (List[Tuple[str, str]]): List of attribute name and value pairs.
        """
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.links.append(value)
        if tag in ["img", "script", "link"]:
            for name, value in attrs:
                if name == "src" or (tag == "link" and name == "href"):
                    self.links.append(value)


def fetch_links_from_url(url: str) -> List[str]:
    """Fetch all links from a given URL.

    Args:
        url (str): The URL to fetch links from.

    Returns:
        List[str]: List of links found on the page.
    """
    try:
        validated_url = valid_url(url)
        response = urllib.request.urlopen(validated_url)
        data = response.read().decode()
        parser = LinkParser()
        parser.feed(data)
        return parser.links
    except Exception as e:
        print(f"ERROR: Unable to fetch data from {validated_url}. Reason: {e}")
        return []


def is_valid_file_link(link: str) -> bool:
    """Check if the link is a valid file link based on its extension.

    Args:
        link (str): The link to check.

    Returns:
        bool: True if valid, False otherwise.
    """
    return any(link.endswith(f".{ext}") for ext in EXTENSIONS)


def process_url(url: str, depth: int, base_domain: str, q, seen: Set[str],
                lock: threading.Lock, rate_limiter, file_stats: Dict[str, int],
                download_dir: Optional[str] = None, scan: bool = False,
                follow_extern: bool = False) -> None:
    """Process a URL, fetch its links, and perform download or scanning actions.

    Args:
        url (str): The URL to process.
        depth (int): Depth of links to follow.
        base_domain (str): The base domain to restrict link following.
        q (Queue): The processing queue.
        seen (Set[str]): Set of URLs already processed.
        lock (threading.Lock): Thread lock for shared resources.
        rate_limiter (RateLimiter): RateLimiter object.
        file_stats (Dict[str, int]): File statistics dictionary.
        download_dir (Optional[str], optional): Directory to save downloaded files. Defaults to None.
        scan (bool, optional): Whether to scan only. Defaults to False.
        follow_extern (bool): Whether to follow external links.
    """
    if url in seen:
        return

    with lock:
        seen.add(url)

    print(f"INFO: Accessing {url}")

    rate_limiter.wait()

    links = fetch_links_from_url(url)

    file_links = [link for link in links if is_valid_file_link(link)]

    if download_dir and not scan:
        for file_link in file_links:
            download_file(file_link, download_dir)
    elif scan:
        for file_link in file_links:
            extension = os.path.splitext(file_link)[-1].lstrip('.')
            with lock:
                file_stats[extension] = file_stats.get(extension, 0) + 1

    if depth > 0:
        for link in links:
            parsed_link = urlparse(link)
            joined_link = urljoin(url, link)

            if not follow_extern and parsed_link.netloc and parsed_link.netloc != base_domain:
                continue

            q.put((joined_link, depth - 1, base_domain, follow_extern))


class RateLimiter:
    """Rate limiter class to control the frequency of function calls."""

    def __init__(self, rate: float):
        """
        Initialize a RateLimiter instance.

        :param rate: Number of allowed function calls per second.
        """
        self.rate = rate
        self.last_call = 0.0
        self.lock = threading.Lock()

    def wait(self) -> None:
        """Pause the current thread to maintain the desired rate."""
        with self.lock:
            elapsed = time.time() - self.last_call
            left_to_wait = 1.0 / self.rate - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            self.last_call = time.time()


def download_file(url: str, download_dir: str) -> None:
    """Download a file from a given URL and save it to a specified directory.

    Args:
        url (str): URL of the file to be downloaded.
        download_dir (str): Directory where the file should be saved.
    """
    try:
        validated_url = valid_url(url)
        local_filename = os.path.join(download_dir, os.path.basename(urlparse(validated_url).path))
        with urllib.request.urlopen(validated_url) as response, open(local_filename, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"INFO: Downloaded {validated_url} to {local_filename}")
    except Exception as e:
        print(f"ERROR: Failed to download {validated_url}. Reason: {e}")


def worker_thread(q: 'queue.Queue[Tuple[str, int, str, bool]]',
                  seen: Set[str],
                  lock: threading.Lock,
                  rate_limiter: RateLimiter,
                  file_stats: Dict[str, int],
                  download_dir: Optional[str] = None,
                  scan: bool = False) -> None:
    """
    Worker thread function to process URLs from the queue.

    Args:
        q: Queue containing URLs to process.
        seen: Set of already processed URLs.
        lock: Lock object to ensure thread-safe access to shared resources.
        rate_limiter: Instance to control the rate of requests.
        file_stats: Dictionary tracking statistics about processed files.
        download_dir: Directory where files should be saved; if None, no download occurs.
        scan: Indicates whether the tool is in scan mode or not.
    """
    while True:
        task = q.get()
        if task is None:
            break

        url, depth, base_domain, follow_extern = task
        process_url(url, depth, base_domain, q, seen, lock, rate_limiter, file_stats, download_dir, scan, follow_extern)

        q.task_done()


def valid_url(url: str) -> str:
    """Validates if the provided value is a valid URL.

    Args:
        url (str): The string to validate.

    Returns:
        str: The validated URL.

    Raises:
        argparse.ArgumentTypeError: If the provided string is not a valid URL.
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    if not url_pattern.match(url):
        raise argparse.ArgumentTypeError(f"'{url}' is not a valid URL.")
    return url


def main():
    show_banner()
    check_exiftool_installed()

    parser = argparse.ArgumentParser(description="Retrieve and display metadata from files using exiftool.",
                                     epilog="Example commands:\n"
                                            "  python3 MetaDetective.py -d directory\n"
                                            "  python3 MetaDetective.py -d directory -i ^admin anonymous -t doc pdf\n"
                                            "  python3 MetaDetective.py -d directory -t all -display singular -format formatted\n"
                                            "  python3 MetaDetective.py -d directory --export\n"
                                            "\n"
                                            "  python3 MetaDetective.py --scrapper --scan --url https://example.com/\n"
                                            "  python3 MetaDetective.py --scrapper --download-dir directory --url https://example.com/\n"
                                            "  python3 MetaDetective.py --scrapper --depth 1 --download-dir directory --url https://example.com/\n",
                                     formatter_class=argparse.RawTextHelpFormatter
                                     )

    webscraper_group = parser.add_argument_group('Scrapper options', 'Metadata scrapper options.')
    webscraper_group.add_argument('-s', '--scrapper', action='store_true', help="Option required to use the scrapper.")
    webscraper_group.add_argument('-u', "--url", type=valid_url, help="The URL to scan.")
    webscraper_group.add_argument("--scan", action="store_true", help="Scan and display file statistics without downloading.")
    webscraper_group.add_argument("--depth", type=int, default=0, help="Depth of links to follow.")
    webscraper_group.add_argument("--download-dir", type=valid_directory, help="Directory to save downloaded files.")
    webscraper_group.add_argument("--follow-extern", action="store_true", help="Follow external links.")
    webscraper_group.add_argument("--threads", type=int, default=4, help="Number of threads to use.")
    webscraper_group.add_argument("--rate", type=int, default=5, help="Maximum requests per second.")

    analysis_group = parser.add_argument_group('analysis options', 'Analysis options for MetaDetective.')
    analysis_group.add_argument('-d', '--directory', type=valid_directory, help="Directory to analyze.")
    analysis_group.add_argument('-f', '--files', nargs='+', help="File or list of files to analyze.")
    analysis_group.add_argument('-t', '--type', nargs='+', default=['all'], help="File extension(s) or 'all' for all files.")

    display_group = parser.add_argument_group('display options', 'Options affecting how metadata is displayed')
    display_group.add_argument('-i', '--ignore', nargs='+', help="Ignore specific items in display using regex or words.")
    display_group.add_argument('-display', choices=['all', 'singular'], default='singular', help="Display mode: 'all' or 'singular'")
    display_group.add_argument('-format', choices=['formatted', 'concise'], help="Display format for 'singular' mode: 'formatted' or 'concise'")

    export_group = parser.add_argument_group('export options', 'Options for exporting metadata')
    export_group.add_argument('-e', '--export', nargs='?', const='html', choices=['html', 'txt'], default=None, help="Export results. Optional formats: 'html' or 'txt'. If not specified, 'html' is the default.")
    export_group.add_argument('-c', '--custom', type=valid_filename, help="Add a custom suffix to the export filename. It should be alphanumeric and less than 16 characters.")
    export_group.add_argument('-o', '--output', type=valid_directory, default=os.getcwd(), help="Specify a custom output directory for the exported file.")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    if args.scrapper:
        if args.directory or args.files or args.ignore:
            print("ERROR: --directory, --files, and --ignore cannot be used with --scrapper.")
            sys.exit(1)

        if not args.url:
            print("ERROR: --url is required when using --scrapper.")
            sys.exit(1)

        if args.scan and args.download_dir:
            print("ERROR: Use either --scan or --download-dir with --scrapper, but not both.")
            sys.exit(1)
        elif not args.scan and not args.download_dir:
            print("ERROR: You must specify either --scan or --download-dir with --scrapper.")
            sys.exit(1)

        base_domain = urlparse(args.url).netloc

        seen = set()
        lock = threading.Lock()
        q = queue.Queue()
        rate_limiter = RateLimiter(args.rate)
        file_stats = {}

        q.put((args.url, args.depth, base_domain, args.follow_extern))

        threads = []
        for _ in range(args.threads):
            t = threading.Thread(target=worker_thread, args=(q, seen, lock, rate_limiter, file_stats, args.download_dir, args.scan))
            t.start()
            threads.append(t)

        q.join()

        for _ in range(args.threads):
            q.put(None)
        for t in threads:
            t.join()

        if args.scan:
            print("")
            if len(file_stats) > 0:
                print("Statistics on files found:")
                for ext, count in file_stats.items():
                    print(f"{ext}: {count} files")
            if len(file_stats) > 0:
                print("")
            print(f"INFO: Total URLs processed: {len(seen)}")

        sys.exit(0)

    elif args.directory or args.files:
        if args.directory and args.files:
            print("ERROR: Specify either --directory or --files, but not both.")
            sys.exit(1)

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

    else:
        print("ERROR: You must specify either --scrapper or --directory or --files.")
        sys.exit(1)


if __name__ == "__main__":
    main()
