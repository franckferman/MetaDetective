#!/usr/bin/env python3

"""Unleash Metadata Intelligence with MetaDetective. Your Assistant Beyond Metagoofil.

Created By  : Franck FERMAN @franckferman
Created Date: 27/08/23
Version     : 1.0.9 (09/11/23)
Refactored  : Enhanced multithreading and code structure
"""

import argparse
import datetime
import hashlib
import http.client
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
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin, quote


# Constants
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

EXIFTOOL_NOT_INSTALLED = "Error: exiftool is not installed. Please install it to continue."
EXIFTOOL_EXECUTION_ERROR = "Error: exiftool encountered an error."

NOMINATIM_HOST = "nominatim.openstreetmap.org"
USER_AGENT = 'MetaDetective/1.0.9'
NOMINATIM_ENDPOINT = "/reverse?format=jsonv2&lat={lat}&lon={lon}"
NOMINATIM_LINK = "https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat}&lon={lon}"
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/ui/search.html?q="

# Configuration constants
DEFAULT_HTTP_TIMEOUT = 30
DEFAULT_WORKER_TIMEOUT = 1.0
DEFAULT_SHUTDOWN_TIMEOUT = 5.0
DEFAULT_RATE_LIMIT = 5
DEFAULT_NUM_THREADS = 4
MAX_FILENAME_LENGTH = 16
MAX_RETRIES = 3

CSS_STYLE = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap');

    body {
        font-family: 'Roboto', 'Helvetica', 'Arial', sans-serif;
        color: #EAEAEA;
        padding: 20px;
        margin: 0;
        background: linear-gradient(120deg, #121212, #1E1E1E, #121212);
        background-size: 300% 300%;
        animation: gradientBG 15s ease infinite;
    }

    @keyframes gradientBG {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    .header {
        background-color: rgba(51, 51, 51, 0.8);
        color: white;
        padding: 10px 0;
        text-align: center;
        border-radius: 5px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5);
        text-shadow: 2px 2px 2px rgba(0, 0, 0, 0.2);
    }

    .metadata-entry {
        background-color: rgba(30, 30, 30, 0.8);
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.6);
        transition: all 0.3s ease;
        opacity: 0;
        transform: translateY(-20px);
        animation: fadeInUp 0.5s forwards 0.2s ease-out;
    }

    @keyframes fadeInUp {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .metadata-entry:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.8);
        transform: scale(1.02);
    }

    p {
        margin: 5px 0;
        text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.1);
    }

    strong {
        color: #EAEAEA;
    }

    h3 {
        color: #BBB;
        border-bottom: 1px solid #444;
        padding-bottom: 10px;
        text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.1);
    }

    hr {
        border: 0;
        border-top: 1px solid #333;
        margin-top: 10px;
    }

    a {
        transition: all 0.3s;
    }

    a:link, a:visited {
        color: #BBB;
        text-decoration: none;
    }

    a:hover {
        color: #FFF;
        text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.2);
        text-decoration: underline;
    }

    a:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.5);
    }
    </style>
"""


# ============================================================================
# Logging and Output Utilities
# ============================================================================

class Logger:
    """Simple logging utility for structured output."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"

    @staticmethod
    def log(level: str, message: str, file=None) -> None:
        """
        Log a message with a specific level.

        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Message to log
            file: File to write to (default: sys.stdout for INFO, sys.stderr for ERROR/WARNING)
        """
        if file is None:
            file = sys.stderr if level in (Logger.ERROR, Logger.WARNING) else sys.stdout
        print(f"{level}: {message}", file=file)

    @staticmethod
    def info(message: str) -> None:
        """Log an info message."""
        Logger.log(Logger.INFO, message, sys.stdout)

    @staticmethod
    def warning(message: str) -> None:
        """Log a warning message."""
        Logger.log(Logger.WARNING, message, sys.stderr)

    @staticmethod
    def error(message: str) -> None:
        """Log an error message."""
        Logger.log(Logger.ERROR, message, sys.stderr)


# ============================================================================
# Utility Classes and Functions
# ============================================================================

class RateLimiter:
    """Rate limiter to control the frequency of HTTP requests."""

    def __init__(self, rate: float):
        """
        Initialize a RateLimiter instance.

        Args:
            rate (float): Number of allowed requests per second.
        """
        if rate <= 0:
            raise ValueError("Rate must be positive")
        self.rate = rate
        self.min_interval = 1.0 / rate
        self.last_call = 0.0
        self.lock = threading.Lock()

    def wait(self) -> None:
        """Pause the current thread to maintain the desired rate."""
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_call
            wait_time = self.min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            self.last_call = time.time()


class FileStats:
    """Thread-safe container for file statistics."""

    def __init__(self):
        """Initialize empty file statistics."""
        self._stats: Dict[str, Set[Tuple[str, str]]] = {}
        self._lock = threading.Lock()

    def add_file(self, extension: str, url: str, filename: str) -> None:
        """Add a file to the statistics.

        Args:
            extension: File extension
            url: File URL
            filename: File name
        """
        with self._lock:
            if extension not in self._stats:
                self._stats[extension] = set()
            self._stats[extension].add((url, filename))

    def get_stats(self) -> Dict[str, Set[Tuple[str, str]]]:
        """Get a copy of the statistics.

        Returns:
            Dictionary mapping extensions to sets of (url, filename) tuples
        """
        with self._lock:
            return {ext: files.copy() for ext, files in self._stats.items()}

    def has_files(self) -> bool:
        """Check if any files have been recorded.

        Returns:
            True if files exist, False otherwise
        """
        with self._lock:
            return bool(self._stats)


class URLNormalizer:
    """Normalizes URLs to avoid duplicates (removes fragments, normalizes query params)."""

    @staticmethod
    def normalize(url: str) -> str:
        """
        Normalize a URL by removing fragments and sorting query parameters.

        Args:
            url: URL to normalize

        Returns:
            Normalized URL
        """
        try:
            parsed = urlparse(url)
            # Remove fragment and normalize
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                # Optionally sort query parameters for consistency
                # For now, just include them as-is
                normalized += f"?{parsed.query}"
            # Always remove fragment to avoid duplicates
            return normalized.rstrip('/')
        except Exception:
            # If parsing fails, return original URL
            return url


class URLSet:
    """Thread-safe set for tracking processed URLs with normalization."""

    def __init__(self, normalize_urls: bool = True):
        """
        Initialize empty URL set.

        Args:
            normalize_urls: Whether to normalize URLs before adding them
        """
        self._urls: Set[str] = set()
        self._lock = threading.Lock()
        self._normalize = normalize_urls

    def add(self, url: str) -> bool:
        """Add a URL to the set if not already present.

        Args:
            url: URL to add

        Returns:
            True if URL was added, False if it was already present
        """
        if self._normalize:
            url = URLNormalizer.normalize(url)

        with self._lock:
            if url in self._urls:
                return False
            self._urls.add(url)
            return True

    def __contains__(self, url: str) -> bool:
        """Check if URL is in the set.

        Args:
            url: URL to check

        Returns:
            True if URL is in the set, False otherwise
        """
        if self._normalize:
            url = URLNormalizer.normalize(url)

        with self._lock:
            return url in self._urls

    def __len__(self) -> int:
        """Get the number of URLs in the set.

        Returns:
            Number of URLs
        """
        with self._lock:
            return len(self._urls)


# ============================================================================
# Metadata Extraction Classes
# ============================================================================

class MetadataExtractor:
    """Handles metadata extraction from files using exiftool."""

    @staticmethod
    def get_metadata(file_path: str, fields: List[str]) -> dict:
        """
        Retrieve specified metadata fields from a file using exiftool.

        Args:
            file_path: Path of the file to analyze
            fields: List of metadata fields to extract

        Returns:
            Dictionary containing the extracted metadata
        """
        try:
            exiftool_output = subprocess.run(
                ["exiftool", file_path],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            Logger.error(f"Error executing exiftool for {file_path}: {e}")
            return {}
        except UnicodeDecodeError as e:
            Logger.error(f"Error decoding output for file {file_path}: {e}")
            return {}

        field_set = set(fields)
        metadata = {}

        for line in exiftool_output.stdout.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            if key in field_set and value.strip():
                metadata[key] = value.strip()

        # Process GPS data
        GPSProcessor.process_gps_data(metadata)

        return metadata


class GPSProcessor:
    """Handles GPS coordinate processing and formatting."""

    @staticmethod
    def dms_to_dd(degrees: int, minutes: int, seconds: float, direction: str) -> float:
        """
        Convert coordinates from DMS (Degree-Minute-Second) to DD (Decimal Degrees).

        Args:
            degrees: Degrees component of DMS
            minutes: Minutes component of DMS
            seconds: Seconds component of DMS
            direction: Hemisphere identifier ('N', 'S', 'E', 'W')

        Returns:
            Coordinate in Decimal Degrees format
        """
        if not (0 <= degrees < 180) or not (0 <= minutes < 60) or not (0 <= seconds < 60):
            raise ValueError("Invalid DMS values provided.")

        direction = direction.upper()
        if direction not in ['N', 'S', 'E', 'W']:
            raise ValueError("Invalid direction. Expected one of ['N', 'S', 'E', 'W'].")

        dd = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
        if direction in ['S', 'W']:
            dd *= -1
        return dd

    @staticmethod
    def parse_dms(dms_str: str) -> Tuple[int, int, float, str]:
        """
        Parse a DMS (Degree-Minute-Second) string into its components.

        Args:
            dms_str: String in DMS format, e.g., "50 deg 49' 8.59\" N"

        Returns:
            Tuple of (degrees, minutes, seconds, direction)
        """
        match = re.search(r"(\d+)\s*deg\s*(\d+)'\s*([\d.]+)\"\s*(\w)", dms_str)
        if match:
            deg, min, sec, dir = match.groups()

            if dir.upper() not in ['N', 'S', 'E', 'W']:
                raise ValueError(f"Invalid direction: {dir}")

            return int(deg), int(min), float(sec), dir.upper()

        raise ValueError(f"Invalid DMS format: {dms_str}")

    @staticmethod
    def process_gps_data(metadata: Dict[str, str]) -> None:
        """Process GPS data in metadata dictionary.

        Args:
            metadata: Metadata dictionary to process (modified in-place)
        """
        lat_dd, lon_dd = None, None
        gps_position = metadata.get("GPS Position", None)

        if gps_position:
            try:
                lat_str, lon_str = gps_position.split(", ")
                lat_dd = GPSProcessor.dms_to_dd(*GPSProcessor.parse_dms(lat_str))
                lon_dd = GPSProcessor.dms_to_dd(*GPSProcessor.parse_dms(lon_str))
            except (ValueError, IndexError) as e:
                Logger.warning(f"Error parsing GPS Position: {e}")
        else:
            gps_lat = metadata.get("GPS Latitude", None)
            gps_lon = metadata.get("GPS Longitude", None)
            if gps_lat and gps_lon:
                try:
                    lat_dd = GPSProcessor.dms_to_dd(*GPSProcessor.parse_dms(gps_lat))
                    lon_dd = GPSProcessor.dms_to_dd(*GPSProcessor.parse_dms(gps_lon))
                except ValueError as e:
                    Logger.warning(f"Error parsing GPS coordinates: {e}")

        if lat_dd is not None and lon_dd is not None:
            metadata["Formatted GPS Position"] = f"{lat_dd:.6f}, {lon_dd:.6f}"


class AddressResolver:
    """Handles address resolution from GPS coordinates with caching."""

    # Class-level cache to avoid repeated requests for same coordinates
    _cache: Dict[Tuple[str, str], str] = {}
    _cache_lock = threading.Lock()

    @classmethod
    def get_address_from_coords(cls, lat: str, lon: str, timeout: int = DEFAULT_HTTP_TIMEOUT) -> str:
        """
        Fetch address from latitude and longitude using the Nominatim API.
        Uses caching to avoid repeated requests for the same coordinates.

        Args:
            lat: Latitude as a string
            lon: Longitude as a string
            timeout: Connection timeout in seconds

        Returns:
            Address as a string, or empty string if error
        """
        # Normalize coordinates for caching (round to 6 decimal places)
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            lat_normalized = f"{lat_float:.6f}"
            lon_normalized = f"{lon_float:.6f}"
            cache_key = (lat_normalized, lon_normalized)
        except ValueError:
            # If coordinates can't be normalized, use as-is
            cache_key = (lat, lon)
            lat_normalized = lat
            lon_normalized = lon

        # Check cache first
        with cls._cache_lock:
            if cache_key in cls._cache:
                return cls._cache[cache_key]

        # Fetch from API
        try:
            conn = http.client.HTTPSConnection(NOMINATIM_HOST, timeout=timeout)
            headers = {'User-Agent': USER_AGENT}
            endpoint = NOMINATIM_ENDPOINT.format(lat=lat_normalized, lon=lon_normalized)
            conn.request("GET", endpoint, headers=headers)

            res = conn.getresponse()
            data = res.read()
            conn.close()

            parsed_data = json.loads(data.decode("utf-8"))
            address = parsed_data.get("display_name", "")

            # Cache the result
            with cls._cache_lock:
                cls._cache[cache_key] = address

            return address

        except (http.client.HTTPException, json.JSONDecodeError, Exception) as e:
            Logger.error(f"Error fetching address for coordinates {lat}, {lon}: {e}")
            return ""

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the address cache."""
        with cls._cache_lock:
            cls._cache.clear()

    @staticmethod
    def format_gps_data(metadata: Dict[str, str]) -> None:
        """
        Update the provided metadata dictionary with address and map link.

        Args:
            metadata: Metadata dictionary (modified in-place)
        """
        formatted_gps = metadata.get("Formatted GPS Position")
        if not formatted_gps:
            return

        try:
            lat, lon = formatted_gps.split(", ")
        except ValueError:
            Logger.warning("Invalid GPS position format")
            return

        address = AddressResolver.get_address_from_coords(lat, lon)
        if address:
            metadata["Address"] = address

        metadata["Map Link"] = NOMINATIM_LINK.format(lat=lat, lon=lon)


# ============================================================================
# Web Scraping Classes
# ============================================================================

class LinkParser(HTMLParser):
    """HTML Parser to extract links from a web page."""

    def __init__(self) -> None:
        """Initialize the LinkParser."""
        super().__init__()
        self.links: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        """Handle the start tag of an HTML element.

        Args:
            tag: The tag name of the HTML element
            attrs: List of attribute name and value pairs
        """
        tag_to_attr = {
            'a': 'href',
            'img': 'src',
            'script': 'src',
            'link': 'href'
        }

        target_attr = tag_to_attr.get(tag)
        if target_attr:
            for name, value in attrs:
                if name == target_attr:
                    self.links.append(value)


class WebScraper:
    """Handles web scraping operations."""

    def __init__(self, extensions: List[str]):
        """
        Initialize WebScraper.

        Args:
            extensions: List of file extensions to filter (without leading dot)
        """
        # Normalize extensions: remove leading dots and convert to lowercase
        # Filter out empty extensions
        self.extensions = {ext.lstrip('.').lower() for ext in extensions if ext.strip()}
        if not self.extensions:
            # If no valid extensions, use all default extensions
            self.extensions = {ext.lower() for ext in EXTENSIONS}
        self.css_js_pattern = re.compile(r"\.(css|js)($|\?|#)")

    def fetch_links_from_url(self, url: str, timeout: int = DEFAULT_HTTP_TIMEOUT) -> List[str]:
        """
        Fetch all links from a given URL.

        Args:
            url: The URL to fetch links from
            timeout: Request timeout in seconds

        Returns:
            List of links found on the page
        """
        try:
            request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content_type = response.headers.get('Content-Type', '').split(';')[0]
                if 'text' not in content_type and 'application' not in content_type:
                    return []

                # Read the response data once
                raw_data = response.read()

                # Try to decode the response
                try:
                    data = raw_data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        data = raw_data.decode('latin-1')
                    except UnicodeDecodeError:
                        Logger.warning(f"Unable to decode content from {url}")
                        return []

                parser = LinkParser()
                parser.feed(data)
                # Filter out invalid links
                filtered_links = []
                for link in parser.links:
                    # Skip JavaScript, mailto, tel, and other non-HTTP schemes
                    if link.startswith(('javascript:', 'mailto:', 'tel:', 'ftp:', 'data:')):
                        continue
                    # Skip CSS and JS files
                    if self.css_js_pattern.search(link):
                        continue
                    # Skip empty links
                    if not link or link.strip() == '':
                        continue
                    filtered_links.append(link)
                return filtered_links

        except urllib.error.URLError as e:
            if url.startswith("mailto:"):
                Logger.info(f"Found mailto link {url}")
            else:
                Logger.error(f"Unable to open {url} Reason: {e}")
            return []
        except urllib.error.HTTPError as e:
            Logger.error(f"HTTP Error for URL {url} Reason: {e.code} - {e.reason}")
            return []
        except Exception as e:
            Logger.error(f"Unexpected error fetching {url} Reason: {e}")
            return []

    def is_valid_file_link(self, link: str) -> bool:
        """
        Check if the link is a valid file link based on its extension.

        Args:
            link: The link to check

        Returns:
            True if valid, False otherwise
        """
        if not link or not self.extensions:
            return False

        path = urlparse(link).path
        if not path:
            return False

        # Extract extension (remove leading dot and convert to lowercase)
        extension = os.path.splitext(path)[1].lstrip('.').lower()
        return extension in self.extensions


class FileDownloader:
    """Handles file downloading operations."""

    @staticmethod
    def calculate_hash(data: bytes) -> str:
        """
        Calculate the SHA-256 hash of the given data.

        Args:
            data: The binary content of the data to be hashed

        Returns:
            The hexadecimal digest of the SHA-256 hash
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data)
        return sha256_hash.hexdigest()

    @staticmethod
    def find_unique_filename(path: str) -> str:
        """
        Generate a unique filename by appending a numeric suffix if needed.

        Args:
            path: The initial file path

        Returns:
            A unique file path
        """
        counter = 2
        base, ext = os.path.splitext(path)
        while os.path.exists(path):
            path = f"{base}-{counter}{ext}"
            counter += 1
        return path

    @staticmethod
    def download_file(url: str, download_dir: str, timeout: int = DEFAULT_HTTP_TIMEOUT) -> None:
        """
        Download a file from a specified URL and save it to the given directory.

        Args:
            url: The URL from which the file will be downloaded
            download_dir: The directory path where the file will be saved
            timeout: Request timeout in seconds
        """
        try:
            # Ensure download directory exists
            os.makedirs(download_dir, exist_ok=True)

            encoded_url = quote(url, safe=":/?&=")
            parsed_path = urlparse(encoded_url).path
            filename = os.path.basename(parsed_path)

            # Use a default filename if none is found
            if not filename:
                filename = "downloaded_file"

            local_filename = os.path.join(download_dir, filename)

            # Create request with user agent
            request = urllib.request.Request(encoded_url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = response.read()
                file_hash = FileDownloader.calculate_hash(data)

                if os.path.exists(local_filename):
                    with open(local_filename, 'rb') as existing_file:
                        existing_file_hash = FileDownloader.calculate_hash(existing_file.read())

                    if file_hash == existing_file_hash:
                        Logger.warning(f"Duplicate file detected for '{local_filename}'. Both have the same hash: {file_hash}.")
                        return
                    else:
                        new_local_filename = FileDownloader.find_unique_filename(local_filename)
                        Logger.info(f"File '{local_filename}' already exists with a different hash. Saving the new file as '{new_local_filename}'.")
                        local_filename = new_local_filename

                with open(local_filename, 'wb') as out_file:
                    out_file.write(data)
                Logger.info(f"Downloaded {url} to {local_filename}. SHA-256: {file_hash}.")
        except urllib.error.HTTPError as e:
            Logger.error(f"HTTP error downloading {url}: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            Logger.error(f"URL error downloading {url}: {e}")
        except Exception as e:
            Logger.error(f"Failed to download {url}. Reason: {e}")


# ============================================================================
# Web Scraping Worker Classes
# ============================================================================

class ScrapingTask:
    """Represents a scraping task."""

    def __init__(self, url: str, depth: int, base_domain: str, follow_extern: bool):
        """
        Initialize a scraping task.

        Args:
            url: URL to process
            depth: Remaining depth
            base_domain: Base domain for filtering
            follow_extern: Whether to follow external links
        """
        self.url = url
        self.depth = depth
        self.base_domain = base_domain
        self.follow_extern = follow_extern


class URLProcessor:
    """Processes URLs during web scraping."""

    def __init__(
        self,
        scraper: WebScraper,
        rate_limiter: RateLimiter,
        file_stats: FileStats,
        download_dir: Optional[str] = None,
        scan: bool = False
    ):
        """
        Initialize URL processor.

        Args:
            scraper: WebScraper instance
            rate_limiter: RateLimiter instance
            file_stats: FileStats instance
            download_dir: Directory for downloads (None if scan mode)
            scan: Whether in scan mode
        """
        self.scraper = scraper
        self.rate_limiter = rate_limiter
        self.file_stats = file_stats
        self.download_dir = download_dir
        self.scan = scan

    def process_url(self, task: ScrapingTask, task_queue: queue.Queue) -> None:
        """
        Process a URL task.

        Args:
            task: ScrapingTask to process
            task_queue: Queue to add new tasks to
        """
        Logger.info(f"Accessing {task.url}")

        self.rate_limiter.wait()

        links = self.scraper.fetch_links_from_url(task.url)

        # Extract file links (convert relative to absolute URLs)
        file_links = []
        for link in links:
            if self.scraper.is_valid_file_link(link):
                absolute_url = urljoin(task.url, link)
                file_links.append(absolute_url)

        # Process file links (download or scan)
        if self.download_dir and not self.scan:
            for file_link in file_links:
                FileDownloader.download_file(file_link, self.download_dir)
        elif self.scan:
            for file_link in file_links:
                file_name = os.path.basename(urlparse(file_link).path)
                extension = os.path.splitext(file_name)[-1].lstrip('.').lower()  # Normalize to lowercase
                if extension:
                    self.file_stats.add_file(extension, file_link, file_name)

        # Process links for further crawling
        if task.depth > 0:
            for link in links:
                # Skip file links as we've already processed them
                if self.scraper.is_valid_file_link(link):
                    continue

                # Skip non-HTTP/HTTPS URLs (tel:, mailto:, javascript:, etc.)
                if not link.startswith(('http://', 'https://', '/')):
                    continue

                absolute_link = urljoin(task.url, link)
                parsed_link = urlparse(absolute_link)

                # Validate that it's an HTTP/HTTPS URL
                if parsed_link.scheme not in ('http', 'https'):
                    continue

                # Check if we should follow external links
                if not task.follow_extern and parsed_link.netloc and parsed_link.netloc != task.base_domain:
                    continue

                task_queue.put(ScrapingTask(absolute_link, task.depth - 1, task.base_domain, task.follow_extern))


class ScrapingWorker:
    """Worker thread for processing scraping tasks."""

    def __init__(
        self,
        task_queue: queue.Queue,
        url_processor: URLProcessor,
        processed_urls: URLSet,
        stop_event: threading.Event,
        worker_id: int
    ):
        """
        Initialize scraping worker.

        Args:
            task_queue: Queue containing tasks to process
            url_processor: URLProcessor instance
            processed_urls: URLSet to track processed URLs
            stop_event: Event to signal worker to stop
            worker_id: Unique identifier for this worker
        """
        self.task_queue = task_queue
        self.url_processor = url_processor
        self.processed_urls = processed_urls
        self.stop_event = stop_event
        self.worker_id = worker_id
        self.errors = 0

    def run(self) -> None:
        """Main worker loop."""
        while not self.stop_event.is_set():
            try:
                task = self.task_queue.get(timeout=DEFAULT_WORKER_TIMEOUT)
            except queue.Empty:
                continue

            try:
                # Check for sentinel (None indicates stop)
                if task is None:
                    self.task_queue.task_done()
                    break

                # Skip if already processed or invalid task
                if not isinstance(task, ScrapingTask):
                    self.task_queue.task_done()
                    continue

                # Skip if already processed
                if task.url in self.processed_urls:
                    self.task_queue.task_done()
                    continue

                # Mark as processed and process
                if self.processed_urls.add(task.url):
                    try:
                        self.url_processor.process_url(task, self.task_queue)
                    except KeyboardInterrupt:
                        # Re-raise keyboard interrupt to allow proper cleanup
                        raise
                    except Exception as e:
                        self.errors += 1
                        Logger.error(f"Worker {self.worker_id} - Exception processing {task.url}: {e}")

                self.task_queue.task_done()
            except Exception as e:
                # Catch any unexpected errors in task processing
                self.errors += 1
                Logger.error(f"Worker {self.worker_id} - Unexpected error: {e}")
                if hasattr(self.task_queue, 'task_done'):
                    try:
                        self.task_queue.task_done()
                    except ValueError:
                        pass  # task_done called more times than items added


class ScrapingManager:
    """Manages web scraping operations with multiple worker threads."""

    def __init__(
        self,
        initial_url: str,
        depth: int,
        follow_extern: bool,
        extensions: List[str],
        rate: int,
        num_threads: int,
        download_dir: Optional[str] = None,
        scan: bool = False
    ):
        """
        Initialize scraping manager.

        Args:
            initial_url: Starting URL
            depth: Maximum depth to crawl
            follow_extern: Whether to follow external links
            extensions: File extensions to filter
            rate: Maximum requests per second
            num_threads: Number of worker threads
            download_dir: Directory for downloads
            scan: Whether in scan mode
        """
        self.initial_url = initial_url
        self.depth = depth
        self.follow_extern = follow_extern
        self.scan = scan

        base_domain = urlparse(initial_url).netloc
        self.initial_task = ScrapingTask(initial_url, depth, base_domain, follow_extern)

        self.scraper = WebScraper(extensions)
        self.rate_limiter = RateLimiter(max(0.1, min(rate, 1000)))  # Limit rate to reasonable range
        self.file_stats = FileStats()
        self.processed_urls = URLSet(normalize_urls=True)  # Enable URL normalization
        self.download_dir = download_dir

        self.url_processor = URLProcessor(
            self.scraper,
            self.rate_limiter,
            self.file_stats,
            download_dir,
            scan
        )

        self.task_queue: queue.Queue = queue.Queue()
        self.stop_event = threading.Event()
        self.workers: List[threading.Thread] = []
        self.num_threads = max(1, min(num_threads, 100))  # Limit threads to reasonable range

    def start(self) -> None:
        """Start the scraping process."""
        # Add initial task
        self.task_queue.put(self.initial_task)

        # Start worker threads
        for i in range(self.num_threads):
            worker = ScrapingWorker(
                self.task_queue,
                self.url_processor,
                self.processed_urls,
                self.stop_event,
                i
            )
            thread = threading.Thread(target=worker.run, name=f"ScrapingWorker-{i}", daemon=False)
            thread.start()
            self.workers.append(thread)

    def wait_for_completion(self) -> None:
        """Wait for all tasks to complete."""
        try:
            # Wait for all tasks to be processed
            self.task_queue.join()
        except KeyboardInterrupt:
            Logger.warning("\nInterrupted by user. Stopping workers...")
            self.stop_event.set()

            # Send sentinels to wake up workers
            for _ in range(self.num_threads):
                try:
                    self.task_queue.put_nowait(None)
                except queue.Full:
                    pass

            # Wait for all workers to finish (with timeout)
            for worker in self.workers:
                worker.join(timeout=DEFAULT_SHUTDOWN_TIMEOUT)
                if worker.is_alive():
                    Logger.warning(f"Worker {worker.name} did not terminate gracefully")
            raise

        # Signal workers to stop
        self.stop_event.set()

        # Send sentinels to wake up workers
        for _ in range(self.num_threads):
            self.task_queue.put(None)

        # Wait for all workers to finish
        for worker in self.workers:
            worker.join()

    def get_results(self) -> Tuple[int, Dict[str, Set[Tuple[str, str]]]]:
        """Get scraping results.

        Returns:
            Tuple of (num_processed_urls, file_stats)
        """
        return len(self.processed_urls), self.file_stats.get_stats()


# ============================================================================
# Display and Export Classes
# ============================================================================

class PatternMatcher:
    """Handles pattern matching for filtering metadata."""

    @staticmethod
    def matches_any_pattern(value: str, patterns: List[str]) -> bool:
        """
        Check if a string matches any of the provided patterns.

        Args:
            value: The string to check
            patterns: List of patterns to check against

        Returns:
            True if the value matches any of the patterns, False otherwise
        """
        if not patterns:
            return False

        compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        return any(pattern.search(value) for pattern in compiled_patterns)


class MetadataDisplay:
    """Handles metadata display operations."""

    @staticmethod
    def display_all_metadata(all_metadata: List[Dict[str, Any]], ignore_patterns: List[str]) -> None:
        """
        Display all metadata fields for each metadata entry.

        Args:
            all_metadata: List of metadata dictionaries to display
            ignore_patterns: Patterns to use for excluding fields
        """
        for metadata in all_metadata:
            AddressResolver.format_gps_data(metadata)

            displayed_fields = 0
            for field, value in metadata.items():
                if field in FIELDS and value and not PatternMatcher.matches_any_pattern(value, ignore_patterns):
                    print(f"{field}: {value}")
                    displayed_fields += 1

            if displayed_fields == 0:
                print("No relevant metadata found.")
            if displayed_fields > 0:
                print("-" * 40)

    @staticmethod
    def display_singular_metadata(
        all_metadata: List[Dict[str, Any]],
        args: Namespace,
        ignore_patterns: List[str]
    ) -> None:
        """
        Display unique metadata fields from a list of metadata entries.

        Args:
            all_metadata: List of metadata dictionaries to process
            args: User arguments, including display format preference
            ignore_patterns: Patterns to use for excluding metadata fields
        """
        unique_values = defaultdict(set)

        for metadata in all_metadata:
            AddressResolver.format_gps_data(metadata)
            for field in UNIQUE_FIELDS:
                value = metadata.get(field, None)
                if field == "Hyperlinks" and value:
                    links = [link.strip() for link in value.split(',')]
                    valid_links = [
                        link for link in links
                        if not PatternMatcher.matches_any_pattern(link, ignore_patterns)
                    ]
                    if valid_links:
                        unique_values[field].add(', '.join(valid_links))
                elif value and not PatternMatcher.matches_any_pattern(value, ignore_patterns):
                    unique_values[field].add(value)

        for field, values in unique_values.items():
            # Deduplicate case-insensitively
            unique_cased_values = {
                next(v for v in values if v.lower() == value.lower()): None
                for value in values
            }.keys()

            if unique_cased_values:
                if args.format == 'formatted':
                    print(f"{field}:")
                    for unique_value in unique_cased_values:
                        print(f"    - {unique_value}")
                else:
                    print(f"{field}: {', '.join(unique_cased_values)}")
                print()

    @staticmethod
    def display_metadata(
        args: Namespace,
        all_metadata: List[Dict[str, Any]],
        ignore_patterns: List[str]
    ) -> None:
        """
        Display metadata based on user's display preference.

        Args:
            args: User arguments indicating the display preference
            all_metadata: List of metadata dictionaries to process
            ignore_patterns: Patterns to use for excluding metadata fields
        """
        if args.display == "all":
            MetadataDisplay.display_all_metadata(all_metadata, ignore_patterns)
        elif args.display == "singular":
            MetadataDisplay.display_singular_metadata(all_metadata, args, ignore_patterns)
        else:
            raise ValueError(f"Unrecognized display preference: {args.display}")


class MetadataExporter:
    """Handles metadata export operations."""

    @staticmethod
    def export_metadata_to_html(
        args: Namespace,
        all_metadata: List[Dict[str, str]],
        ignore_patterns: List[str]
    ) -> str:
        """
        Convert and export metadata to a beautiful HTML page.

        Args:
            args: The parsed command-line arguments
            all_metadata: List of dictionaries containing metadata
            ignore_patterns: List of patterns to ignore

        Returns:
            HTML representation of the metadata
        """
        html_parts = [
            '<html>',
            '<head>',
            '<title>MetaDetective Export</title>',
            CSS_STYLE,
            '</head>',
            '<body>',
            '<div class="header">',
            '<h1>MetaDetective Export Report</h1>',
            '</div>'
        ]

        if args.display == "all":
            for metadata in all_metadata:
                html_parts.append('<div class="metadata-entry">')

                # Format GPS data if present (similar to display_all_metadata)
                formatted_gps = metadata.get("Formatted GPS Position")
                if formatted_gps:
                    try:
                        lat, lon = formatted_gps.split(", ")
                        address = AddressResolver.get_address_from_coords(lat, lon)
                        if address:
                            encoded_address = quote(address)
                            link_to_address = f"{NOMINATIM_SEARCH_URL}{encoded_address}"
                            metadata["Address"] = f"<a href='{link_to_address}' target='_blank' rel='noopener noreferrer'>{address}</a>"
                        metadata["Map Link"] = f"<a href='https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat}&lon={lon}' target='_blank' rel='noopener noreferrer'>View on Map</a>"
                    except ValueError:
                        # If GPS format is invalid, skip address resolution
                        pass

                displayed_fields = 0
                for field, value in metadata.items():
                    if field in FIELDS and value and not PatternMatcher.matches_any_pattern(value, ignore_patterns):
                        html_parts.append(f'<p><strong>{field}:</strong> {value}</p>')
                        displayed_fields += 1

                if displayed_fields == 0:
                    html_parts.append('<p>No relevant metadata found.</p>')

                html_parts.append('<hr></div>')
        elif args.display == "singular":
            unique_values = defaultdict(set)

            for metadata in all_metadata:
                # Format GPS data if present (similar to display_singular_metadata)
                formatted_gps = metadata.get("Formatted GPS Position")
                if formatted_gps:
                    try:
                        lat, lon = formatted_gps.split(", ")
                        address = AddressResolver.get_address_from_coords(lat, lon)
                        if address:
                            encoded_address = quote(address)
                            link_to_address = f"{NOMINATIM_SEARCH_URL}{encoded_address}"
                            # Store address as HTML link (will be processed in unique_values)
                            metadata["Address"] = f"<a href='{link_to_address}' target='_blank' rel='noopener noreferrer'>{address}</a>"
                        map_link = f"https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat}&lon={lon}"
                        metadata["Map Link"] = f"<a href='{map_link}' target='_blank' rel='noopener noreferrer'>View on Map</a>"
                    except ValueError:
                        # If GPS format is invalid, skip address resolution
                        pass

                for field in UNIQUE_FIELDS:
                    value = metadata.get(field, None)
                    if field == "Hyperlinks" and value:
                        links = [link.strip() for link in value.split(',')]
                        valid_links = [
                            link for link in links
                            if not PatternMatcher.matches_any_pattern(link, ignore_patterns)
                        ]
                        if valid_links:
                            unique_values[field].add(', '.join(valid_links))
                    elif value and not PatternMatcher.matches_any_pattern(value, ignore_patterns):
                        unique_values[field].add(value)

            for field, values in unique_values.items():
                unique_cased_values = {
                    next(v for v in values if v.lower() == value.lower()): None
                    for value in values
                }.keys()
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

    @staticmethod
    def export_metadata_to_txt(
        args: Namespace,
        all_metadata: List[Dict[str, Any]],
        ignore_patterns: List[str]
    ) -> str:
        """
        Export the provided metadata to a text format.

        Args:
            args: Arguments specifying the display method and other options
            all_metadata: A list of metadata entries to export
            ignore_patterns: A list of patterns to ignore during the export

        Returns:
            Text representation of the metadata
        """
        if args.display == "all":
            text_parts = MetadataExporter._generate_all_metadata_txt(all_metadata, ignore_patterns)
        elif args.display == "singular":
            text_parts = MetadataExporter._generate_singular_metadata_txt(all_metadata, args, ignore_patterns)
        else:
            text_parts = []

        return '\n'.join(text_parts)

    @staticmethod
    def _generate_all_metadata_txt(all_metadata: List[Dict[str, Any]], ignore_patterns: List[str]) -> List[str]:
        """Generate text representation of all metadata."""
        text_parts = []
        for metadata in all_metadata:
            AddressResolver.format_gps_data(metadata)

            displayed_fields = 0
            for field, value in metadata.items():
                if field in FIELDS and value and not PatternMatcher.matches_any_pattern(value, ignore_patterns):
                    text_parts.append(f"{field}: {value}")
                    displayed_fields += 1

            if displayed_fields == 0:
                text_parts.append("No relevant metadata found.")
            if displayed_fields > 0:
                text_parts.append("-" * 40)

        return text_parts

    @staticmethod
    def _generate_singular_metadata_txt(
        all_metadata: List[Dict[str, Any]],
        args: Namespace,
        ignore_patterns: List[str]
    ) -> List[str]:
        """Generate text representation of unique metadata."""
        text_parts = []
        unique_values = defaultdict(set)

        for metadata in all_metadata:
            AddressResolver.format_gps_data(metadata)
            for field in UNIQUE_FIELDS:
                value = metadata.get(field, None)
                if field == "Hyperlinks" and value:
                    links = [link.strip() for link in value.split(',')]
                    valid_links = [
                        link for link in links
                        if not PatternMatcher.matches_any_pattern(link, ignore_patterns)
                    ]
                    if valid_links:
                        unique_values[field].add(', '.join(valid_links))
                elif value and not PatternMatcher.matches_any_pattern(value, ignore_patterns):
                    unique_values[field].add(value)

        for field, values in unique_values.items():
            unique_cased_values = {
                next(v for v in values if v.lower() == value.lower()): None
                for value in values
            }.keys()
            if unique_cased_values:
                if args.format == 'formatted':
                    text_parts.append(f"{field}:")
                    for unique_value in unique_cased_values:
                        text_parts.append(f"    - {unique_value}")
                else:
                    text_parts.append(f"{field}: {', '.join(unique_cased_values)}")
                text_parts.append("")

        return text_parts


# ============================================================================
# File Operations
# ============================================================================

class FileOperations:
    """Handles file operations."""

    @staticmethod
    def filter_files_by_extension(files: List[str], extensions: List[str]) -> List[str]:
        """
        Filter a list of files to return only those that match the provided extensions.

        Args:
            files: The list of file paths to filter
            extensions: A list of file extensions to filter by

        Returns:
            A filtered list of file paths
        """
        if not isinstance(files, list) or not all(isinstance(f, str) for f in files):
            raise TypeError("The 'files' argument must be a list of strings.")

        if not isinstance(extensions, list) or not all(isinstance(ext, str) for ext in extensions):
            raise TypeError("The 'extensions' argument must be a list of strings.")

        ext_set = set(extensions)
        return [file for file in files if file.endswith(tuple(ext_set))]

    @staticmethod
    def get_files(args) -> List[str]:
        """
        Retrieve a list of files based on the provided arguments.

        Args:
            args: The parsed command-line arguments

        Returns:
            List of file paths
        """
        if args.directory:
            try:
                valid_directory(args.directory)
            except argparse.ArgumentTypeError as e:
                raise ValueError(str(e))

            files = [os.path.join(args.directory, file) for file in os.listdir(args.directory)]
            if args.type != ['all']:
                files = FileOperations.filter_files_by_extension(files, args.type)
        else:
            files = args.files

        if not files:
            raise ValueError("Error: No files found.")

        return files


# ============================================================================
# Validation Functions
# ============================================================================

def valid_directory(path: str) -> str:
    """
    Validate directory path.

    Args:
        path: The directory path to validate

    Returns:
        The valid directory path

    Raises:
        argparse.ArgumentTypeError: If the directory path is invalid
    """
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Directory path '{path}' does not exist.")

    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"Path '{path}' is not a directory.")

    return path


def valid_filename(value: str) -> str:
    """
    Check if the filename is alphanumeric, less than MAX_FILENAME_LENGTH characters, and can contain symbols '-' or '_', but not at the end.

    Args:
        value: The filename suffix to validate

    Returns:
        The valid filename suffix

    Raises:
        argparse.ArgumentTypeError: If the filename suffix is invalid
    """
    if not value or len(value) > MAX_FILENAME_LENGTH:
        raise argparse.ArgumentTypeError(f"Filename suffix must be non-empty and less than {MAX_FILENAME_LENGTH} characters.")

    pattern = r'^[a-zA-Z0-9_-]*[a-zA-Z0-9]$'

    if not re.match(pattern, value):
        raise argparse.ArgumentTypeError("Invalid filename suffix. It should be alphanumeric, can contain '-' or '_', but not end with them.")

    return value


def valid_url(url: str) -> str:
    """
    Validates if the provided value is a valid URL.

    Args:
        url: The string to validate

    Returns:
        The validated URL

    Raises:
        argparse.ArgumentTypeError: If the provided string is not a valid URL
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    if not url_pattern.match(url):
        raise argparse.ArgumentTypeError(f"'{url}' is not a valid URL.")
    return url


# ============================================================================
# Main Functions
# ============================================================================

def show_banner() -> None:
    """Print the banner."""
    print(BANNER)


def check_exiftool_installed() -> None:
    """Verify exiftool installation and exit the program if absent or on execution error."""
    try:
        subprocess.run(["exiftool", "-ver"], capture_output=True, check=True, text=True)
    except FileNotFoundError:
        sys.exit(EXIFTOOL_NOT_INSTALLED)
    except subprocess.CalledProcessError:
        sys.exit(EXIFTOOL_EXECUTION_ERROR)


def main():
    """Main entry point for the application."""
    show_banner()
    check_exiftool_installed()

    parser = argparse.ArgumentParser(
        description="Retrieve and display metadata from files using exiftool.",
        epilog="Example commands:\n\n"
               "# Analysis:\n"
               "   # Analyze metadata in a specified directory:\n"
               "python3 MetaDetective.py -d path/to/directory\n"
               "   # Analyze specific file types in a directory and ignore certain patterns:\n"
               "python3 MetaDetective.py -d directory -i ^admin anonymous -t doc pdf\n"
               "   # Analyze all file types in a directory with formatted display:\n"
               "python3 MetaDetective.py -d directory -t all -display singular -format formatted\n"
               "\n"
               "   # Export metadata analysis of a directory and exports data (by default in HTML format):\n"
               "python3 MetaDetective.py -d directory --export\n"
               "\n"
               "# Scraping:\n"
               "   # Scan a website without downloading files:\n"
               "python3 MetaDetective.py --scraping --scan --url https://example.com/\n"
               "   # Download files from a website to a specified directory:\n"
               "python3 MetaDetective.py --scraping --download-dir directory --url https://example.com/\n"
               "   # Download files from a website with specified depth:\n"
               "python3 MetaDetective.py --scraping --depth 1 --download-dir directory --url https://example.com/\n",
        formatter_class=argparse.RawTextHelpFormatter
    )

    scraping_group = parser.add_argument_group('scraping options', 'Options for scraping files containing potential metadata from a website.')
    scraping_group.add_argument('-s', '--scraping', action='store_true', help="Argument required to activate scraping mode.")
    scraping_group.add_argument('-u', "--url", type=valid_url, help="Site url for scraping.")
    scraping_group.add_argument("--scan", action="store_true", help="Scans the website and displays information and statistics without downloading files.")
    scraping_group.add_argument('--extensions', nargs='+', type=str.lower, help='File extensions to filter by, e.g., --extensions pdf jpg png')
    scraping_group.add_argument("--depth", type=int, default=0, help="Depth of links to follow on the site.")
    scraping_group.add_argument("--download-dir", type=valid_directory, help="Directory where files that have been scraped should be stored.")
    scraping_group.add_argument("--follow-extern", action="store_true", help="Follow external links.")
    scraping_group.add_argument("--threads", type=int, default=DEFAULT_NUM_THREADS, help="Number of threads to use (1-100).")
    scraping_group.add_argument("--rate", type=int, default=DEFAULT_RATE_LIMIT, help="Maximum number of requests per second (0.1-1000).")

    analysis_group = parser.add_argument_group('analysis options', 'Main analysis options.')
    analysis_group.add_argument('-d', '--directory', type=valid_directory, help="Directory containing the files to be analyzed.")
    analysis_group.add_argument('-f', '--files', nargs='+', help="File or space-separated list of files to be analyzed.")
    analysis_group.add_argument('-t', '--type', nargs='+', default=['all'], help="File types (extensions) to be analyzed (all by default).")

    display_group = parser.add_argument_group('display options', 'Options for displaying results.')
    display_group.add_argument('-i', '--ignore', nargs='+', help="Ignore one or more results separated by spaces for keywords or regexes.")
    display_group.add_argument('--display', choices=['all', 'singular'], default='singular', help="Display options:\n'all' to display all relevant results for each file one by one.\n'singular' to display condensed results.'")
    display_group.add_argument('--format', choices=['formatted', 'concise'], help="Display format ('singular' display required):\n'formatted' for a formatted (stylized) display.\n'concise' for more classic (basic) formatting.")

    export_group = parser.add_argument_group('export options', 'Options for exporting results.')
    export_group.add_argument('-e', '--export', nargs='?', const='html', choices=['html', 'txt'], default=None, help="Export results. Default format is HTML. Text export (txt) is also possible.")
    export_group.add_argument('-c', '--custom', type=valid_filename, help="Custom file name. The name is generated with default values, but you can add a suffix.")
    export_group.add_argument('-o', '--out', type=valid_directory, default=os.getcwd(), help="Specify file export directory.")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    if args.scraping:
        if args.directory or args.files or args.ignore:
            parser.error("Analysis arguments (--directory/-d, --files/-f, and --ignore/-i) cannot be used with scrapping options (--scraping/-s).")

        if args.scan and args.download_dir:
            parser.error("The scan (--scan) and download (--download-dir) arguments cannot be specified together. Choose between one or the other mode in scraping mode, but not both.")
        elif not args.scan and not args.download_dir:
            parser.error("You must choose at least between the scan (--scan) or download (--download-dir) argument in scraping mode.")

        if not args.url:
            parser.error("The url choice argument (-u or --url) is required for scraping mode.")

        extensions = args.extensions if args.extensions else EXTENSIONS.copy()

        # Validate threads and rate limits
        if args.threads < 1 or args.threads > 100:
            parser.error(f"Threads must be between 1 and 100, got {args.threads}")
        if args.rate < 1 or args.rate > 1000:
            parser.error(f"Rate must be between 1 and 1000 requests per second, got {args.rate}")
        if args.depth < 0:
            parser.error(f"Depth must be non-negative, got {args.depth}")

        manager = ScrapingManager(
            initial_url=args.url,
            depth=args.depth,
            follow_extern=args.follow_extern,
            extensions=extensions,
            rate=args.rate,
            num_threads=args.threads,
            download_dir=args.download_dir,
            scan=args.scan
        )

        manager.start()
        manager.wait_for_completion()

        if args.scan:
            num_processed, file_stats = manager.get_results()

            if not file_stats:
                print("\nNo files found or no files with specified extensions.")
                sys.exit(0)

            print("\nScan results:\n")
            print("+---------------+-----------------------------------+")
            print("| File Extension | Estimated Number of Unique Files |")
            print("+---------------+-----------------------------------+")
            for ext, files in sorted(file_stats.items()):
                print(f"| {ext.ljust(14)} | {str(len(files)).ljust(32)} |")
            print("+---------------+-----------------------------------+")
            print(f"\nINFO: Total URLs processed (followed): {num_processed}")
            print("NOTE: These results provide an estimation and do not guarantee the uniqueness of the files.")

        sys.exit(0)

    elif args.directory or args.files:
        if args.directory and args.files:
            parser.error("The directory (--directory/-d) and files (--files/-f) arguments cannot be specified together. Choose between one or the other mode in analysis mode, but not both.")

        ignore_patterns = args.ignore if args.ignore else []

        if args.display == 'all' and args.format:
            parser.error("The formatting (--format) argument is not compatible with the 'all' display mode (--display all).")

        if args.display == 'singular' and args.format is None:
            args.format = 'concise'

        files = FileOperations.get_files(args)
        all_metadata = [MetadataExtractor.get_metadata(file, FIELDS) for file in files]

        if args.export:
            if args.export == 'html':
                content = MetadataExporter.export_metadata_to_html(args, all_metadata, ignore_patterns)
                file_extension = '.html'
            else:
                content = MetadataExporter.export_metadata_to_txt(args, all_metadata, ignore_patterns)
                file_extension = '.txt'

            timestamp = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
            custom_suffix = f"{args.custom}-" if args.custom else ""
            filename = f"MetaDetective_Export-{custom_suffix}{timestamp}{file_extension}"

            full_path = os.path.join(args.out, filename)

            with open(full_path, "w", encoding='utf-8') as f:
                f.write(content)
            print(f"Results file exported to {full_path}")
        else:
            MetadataDisplay.display_metadata(args, all_metadata, ignore_patterns)

    else:
        parser.error("You must specify either --scraping or --directory or --files.")


if __name__ == "__main__":
    main()
