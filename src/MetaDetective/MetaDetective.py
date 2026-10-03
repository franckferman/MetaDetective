#!/usr/bin/env python3

"""Unleash Metadata Intelligence with MetaDetective. Your Assistant Beyond Metagoofil.

Created By  : Franck FERMAN @franckferman
Created Date: 27/08/23
Version     : 2.0.6 (03/07/26)
Refactored  : Enhanced multithreading and code structure
"""

import argparse
import datetime
import html
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
import zlib
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
    "doc", "docx", "odt", "pdf", "rtf", "tex", "wpd",
    "heic", "heif"
]

try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("MetaDetective")
except Exception:
    __version__ = "dev"

EXIFTOOL_NOT_INSTALLED = "Error: exiftool is not installed. Please install it to continue."
EXIFTOOL_EXECUTION_ERROR = "Error: exiftool encountered an error."

NOMINATIM_HOST = "nominatim.openstreetmap.org"
NOMINATIM_SCHEME = "https"
GEOCODE_ENABLED = True
USER_AGENT = f'MetaDetective/{__version__}'

UA_PRESETS = {
    'default': USER_AGENT,
    'chrome-win': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'chrome-mac': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'chrome-linux': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'firefox-win': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'firefox-mac': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0',
    'firefox-linux': 'Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'safari-mac': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    'edge-win': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
    'android': 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'iphone': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'googlebot': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'stealth': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}
NOMINATIM_ENDPOINT = "/reverse?format=jsonv2&lat={lat}&lon={lon}"
NOMINATIM_LINK = "https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat}&lon={lon}"
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/ui/search.html?q="

DEFAULT_HTTP_TIMEOUT = 30
DEFAULT_WORKER_TIMEOUT = 1.0
DEFAULT_SHUTDOWN_TIMEOUT = 5.0
DEFAULT_RATE_LIMIT = 5
DEFAULT_NUM_THREADS = 4
DEFAULT_DEPTH = 1
DEFAULT_DOWNLOAD_DIR = "loot"
MAX_FILENAME_LENGTH = 16
MAX_RETRIES = 3

CSS_STYLE = """
    <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{
        --bg:#0c0b0b;--surface:#111010;--surface-h:#161414;
        --border:#201e1e;--red:#b83228;--red-dim:rgba(184,50,40,.10);
        --paper:#c0b49a;--paper-dim:#6e6350;--text:#9e9080;
        --text-bright:#c4b8a4;--mono:'Courier New',Courier,monospace;
    }
    html{scroll-behavior:smooth}
    body{
        background:var(--bg);color:var(--text);font-family:var(--mono);
        font-size:14px;line-height:1.7;padding:0;margin:0;
        border-top:2px solid var(--red);
    }
    .report-wrap{max-width:960px;margin:0 auto;padding:2rem 1.5rem 4rem}
    .header{
        text-align:center;padding:2rem 0 1.5rem;
        border-bottom:1px solid var(--border);margin-bottom:2rem;
    }
    .header h1{
        font-size:1.4rem;letter-spacing:.08em;text-transform:uppercase;
        color:var(--text-bright);margin-bottom:.4rem;
    }
    .header h1 span{color:var(--red)}
    .header .sub{font-size:.75rem;color:var(--paper-dim);letter-spacing:.05em}
    .stats{
        display:flex;gap:1.5rem;flex-wrap:wrap;justify-content:center;
        margin:1.5rem 0;
    }
    .stat{
        background:var(--surface);border:1px solid var(--border);
        padding:.6rem 1.2rem;border-radius:3px;text-align:center;
    }
    .stat-val{font-size:1.3rem;color:var(--red);font-weight:bold}
    .stat-label{font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;color:var(--paper-dim)}
    .metadata-entry{
        background:var(--surface);border:1px solid var(--border);
        border-radius:3px;padding:1rem 1.2rem;margin-bottom:1rem;
        transition:border-color .2s;
    }
    .metadata-entry:hover{border-color:var(--red)}
    .field-row{display:flex;gap:.8rem;padding:.25rem 0;border-bottom:1px solid var(--border)}
    .field-row:last-child{border-bottom:none}
    .field-key{
        color:var(--red);font-size:.75rem;letter-spacing:.08em;
        text-transform:uppercase;min-width:160px;flex-shrink:0;
        padding-top:1px;
    }
    .field-val{color:var(--text-bright);word-break:break-all}
    h3{
        color:var(--red);font-size:.8rem;letter-spacing:.1em;
        text-transform:uppercase;margin:2rem 0 .8rem;
        padding-bottom:.4rem;border-bottom:1px solid var(--border);
    }
    p{margin:.3rem 0;font-size:.85rem}
    ul{list-style:none;padding:0}
    ul li{padding:.2rem 0;color:var(--text-bright);font-size:.85rem}
    ul li::before{content:'>';color:var(--red);margin-right:.5rem;font-weight:bold}
    hr{border:none;border-top:1px solid var(--border);margin:1.5rem 0}
    a{color:var(--paper);text-decoration:none;transition:color .2s}
    a:hover{color:var(--red)}
    .footer{
        text-align:center;margin-top:3rem;padding-top:1rem;
        border-top:1px solid var(--border);
        font-size:.65rem;color:var(--paper-dim);letter-spacing:.05em;
    }
    @media(max-width:600px){
        .report-wrap{padding:1rem}
        .field-row{flex-direction:column;gap:.2rem}
        .field-key{min-width:auto}
        .stats{gap:.8rem}
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
    # Nominatim usage policy: at most 1 request per second, shared across threads
    _rate_limiter = RateLimiter(1.0)

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
        if not GEOCODE_ENABLED:
            return ""

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

        with cls._cache_lock:
            if cache_key in cls._cache:
                return cls._cache[cache_key]

        try:
            cls._rate_limiter.wait()
            if NOMINATIM_SCHEME == "http":
                conn = http.client.HTTPConnection(NOMINATIM_HOST, timeout=timeout)
            else:
                conn = http.client.HTTPSConnection(NOMINATIM_HOST, timeout=timeout)
            headers = {'User-Agent': USER_AGENT}
            endpoint = NOMINATIM_ENDPOINT.format(lat=lat_normalized, lon=lon_normalized)
            conn.request("GET", endpoint, headers=headers)

            res = conn.getresponse()
            data = res.read()
            conn.close()

            parsed_data = json.loads(data.decode("utf-8"))
            address = parsed_data.get("display_name", "")

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
# Browser header import (--curl-file)
# ============================================================================

class CurlParseError(ValueError):
    """Raised when a 'Copy as cURL' command cannot be parsed."""


class CurlProfile:
    """
    Request headers imported from a browser's 'Copy as cURL' command.

    Replaying the exact header set a real browser sends (Accept, Sec-Fetch-*,
    sec-ch-ua, cookies, ...) gets past bot-detection checks that a lone
    User-Agent change does not. Credential headers (cookies, auth, CSRF
    tokens) are only ever sent to the host the command was copied from.
    """

    # Headers that only make sense for the original request, or that would
    # break urllib (it does not decompress gzip/br/zstd, and conditional
    # headers turn responses into bodiless 304s).
    DROPPED_HEADERS = {
        'host', 'content-length', 'connection', 'accept-encoding', 'te',
        'if-none-match', 'if-modified-since', 'if-match', 'if-unmodified-since',
        'if-range', 'range', 'expect', 'transfer-encoding', 'upgrade',
    }

    # Headers that carry credentials and must stay on the source host.
    SENSITIVE_HEADERS = {
        'cookie', 'authorization', 'proxy-authorization',
        'x-csrf-token', 'x-xsrf-token', 'x-csrftoken', 'x-api-key',
    }

    # curl options that consume the next token as their value.
    OPTIONS_WITH_VALUE = {
        '-H', '--header', '-b', '--cookie', '-A', '--user-agent', '-e', '--referer',
        '-X', '--request', '-d', '--data', '--data-raw', '--data-binary',
        '--data-urlencode', '--data-ascii', '-F', '--form', '-o', '--output',
        '-x', '--proxy', '-u', '--user', '-m', '--max-time', '--connect-timeout',
        '--cacert', '--cert', '--key', '-w', '--write-out', '-T', '--upload-file',
        '--resolve', '-r', '--range', '--url', '-c', '--cookie-jar',
    }

    def __init__(self, url: Optional[str], headers: List[Tuple[str, str]]):
        self.url = url
        self.headers = headers
        self.scope_host = urlparse(url).hostname if url else None
        self._opener = None

    # -- Parsing ------------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        Split a POSIX shell command line into words.

        Handles single quotes, double quotes, backslash escapes, line
        continuations and bash ANSI-C quoting ($'...'), which Chrome uses
        when a value contains special characters. shlex lacks the latter.
        """
        tokens: List[str] = []
        current: List[str] = []
        in_token = False
        i, n = 0, len(text)

        while i < n:
            ch = text[i]
            if ch == '\\' and i + 1 < n and text[i + 1] in '\r\n':
                # Line continuation.
                i += 2
                if text[i - 1] == '\r' and i < n and text[i] == '\n':
                    i += 1
                continue
            if ch.isspace():
                if in_token:
                    tokens.append(''.join(current))
                    current, in_token = [], False
                i += 1
                continue
            in_token = True
            if ch == "'":
                end = text.find("'", i + 1)
                if end == -1:
                    raise CurlParseError("Unterminated single quote in curl command.")
                current.append(text[i + 1:end])
                i = end + 1
            elif ch == '"':
                i += 1
                while i < n and text[i] != '"':
                    if text[i] == '\\' and i + 1 < n and text[i + 1] in '"\\$`\n':
                        if text[i + 1] != '\n':
                            current.append(text[i + 1])
                        i += 2
                    else:
                        current.append(text[i])
                        i += 1
                if i >= n:
                    raise CurlParseError("Unterminated double quote in curl command.")
                i += 1
            elif ch == '$' and i + 1 < n and text[i + 1] == "'":
                i += 2
                raw: List[str] = []
                while i < n and text[i] != "'":
                    if text[i] == '\\' and i + 1 < n:
                        raw.append(text[i:i + 2])
                        i += 2
                    else:
                        raw.append(text[i])
                        i += 1
                if i >= n:
                    raise CurlParseError("Unterminated $'...' quote in curl command.")
                i += 1
                try:
                    current.append(''.join(raw).encode('latin-1', 'backslashreplace').decode('unicode_escape'))
                except UnicodeDecodeError as exc:
                    raise CurlParseError(f"Invalid escape sequence in $'...' quote: {exc}")
            elif ch == '\\' and i + 1 < n:
                current.append(text[i + 1])
                i += 2
            else:
                current.append(ch)
                i += 1

        if in_token:
            tokens.append(''.join(current))
        return tokens

    @staticmethod
    def _unescape_cmd(text: str) -> str:
        """
        Convert Chrome's 'Copy as cURL (cmd)' Windows syntax to POSIX syntax.

        cmd.exe escapes every special character with '^' (including the
        quotes: ^"...^") and continues lines with a trailing '^'. Inner
        quotes are written as \\^", which becomes \\" once carets are gone.
        """
        text = re.sub(r'\^\r?\n', ' ', text)
        return re.sub(r'\^(.)', r'\1', text, flags=re.DOTALL)

    @staticmethod
    def _looks_like_cmd(text: str) -> bool:
        return '^"' in text or bool(re.search(r'\^\r?\n', text))

    @classmethod
    def parse(cls, text: str) -> 'CurlProfile':
        """
        Parse a curl command (as produced by browser dev tools) into a profile.

        Args:
            text: The full curl command line

        Returns:
            A CurlProfile with the URL and the headers to replay

        Raises:
            CurlParseError: If the text is not a usable curl command
        """
        text = text.strip()
        if text.startswith('\ufeff'):
            text = text[1:]
        if cls._looks_like_cmd(text):
            text = cls._unescape_cmd(text)

        tokens = cls._tokenize(text)
        if not tokens or os.path.basename(tokens[0]).lower() not in ('curl', 'curl.exe'):
            raise CurlParseError("File does not contain a curl command (it must start with 'curl').")

        url: Optional[str] = None
        headers: List[Tuple[str, str]] = []
        cookies: List[str] = []
        ignored: Set[str] = set()

        i = 1
        while i < len(tokens):
            tok = tokens[i]
            value: Optional[str] = None

            if tok.startswith('--') or tok in cls.OPTIONS_WITH_VALUE:
                opt = tok
            elif tok.startswith('-') and len(tok) > 2 and tok[:2] in cls.OPTIONS_WITH_VALUE:
                # Attached short option value, e.g. -H'Accept: */*'
                opt, value = tok[:2], tok[2:]
            elif tok.startswith('-') and len(tok) > 1:
                opt = tok
            else:
                if url is None:
                    url = tok
                i += 1
                continue

            if opt in cls.OPTIONS_WITH_VALUE and value is None:
                if i + 1 >= len(tokens):
                    raise CurlParseError(f"Option {opt} is missing its value.")
                value = tokens[i + 1]
                i += 1
            i += 1

            if opt in ('-H', '--header'):
                header = cls._parse_header(value)
                if header is None:
                    continue
                if header[0].lower() == 'cookie':
                    cookies.append(header[1])
                else:
                    headers.append(header)
            elif opt in ('-b', '--cookie'):
                if '=' in value:
                    cookies.append(value)
                else:
                    Logger.warning(f"--curl-file: cookie file '{value}' ignored (only inline cookies are supported).")
            elif opt in ('-A', '--user-agent'):
                headers.append(('User-Agent', value))
            elif opt in ('-e', '--referer'):
                headers.append(('Referer', value))
            elif opt == '--url':
                url = value
            elif opt in ('-X', '--request'):
                if value.upper() != 'GET':
                    ignored.add(f"{opt} {value}")
            elif opt in ('-d', '--data', '--data-raw', '--data-binary',
                         '--data-urlencode', '--data-ascii', '-F', '--form', '-T', '--upload-file'):
                ignored.add('request body')
            elif opt in ('-u', '--user'):
                ignored.add(opt)

        if ignored:
            Logger.warning(f"--curl-file: ignored {', '.join(sorted(ignored))}; only headers and cookies are imported.")

        if cookies:
            headers.append(('Cookie', '; '.join(c.strip().rstrip(';') for c in cookies if c.strip())))

        filtered: List[Tuple[str, str]] = []
        for name, val in headers:
            lname = name.lower()
            if lname in cls.DROPPED_HEADERS or name.startswith(':'):
                continue
            # Last occurrence wins, like curl.
            filtered = [(n, v) for n, v in filtered if n.lower() != lname]
            filtered.append((name, val))

        if url is not None and not looks_like_url(url):
            url = None

        return cls(url, filtered)

    @staticmethod
    def _parse_header(raw: str) -> Optional[Tuple[str, str]]:
        """Parse a -H value. Returns None for curl's header-removal syntax."""
        if raw.endswith(';') and ':' not in raw:
            # 'Name;' means send the header with an empty value.
            return raw[:-1].strip(), ''
        if ':' not in raw:
            raise CurlParseError(f"Malformed header (missing ':'): {raw!r}")
        name, _, val = raw.partition(':')
        name, val = name.strip(), val.strip()
        if not name:
            raise CurlParseError(f"Malformed header (empty name): {raw!r}")
        if not val:
            # 'Name:' tells curl to remove the header; nothing to send.
            return None
        return name, val

    @classmethod
    def from_file(cls, path: str) -> 'CurlProfile':
        """
        Load a curl command from a file, or from stdin when path is '-'.

        Raises:
            CurlParseError: If the file cannot be read or parsed
        """
        try:
            if path == '-':
                text = sys.stdin.read()
            else:
                with open(path, 'r', encoding='utf-8-sig') as fh:
                    text = fh.read()
        except OSError as exc:
            raise CurlParseError(f"Cannot read curl file '{path}': {exc.strerror or exc}")
        except UnicodeDecodeError:
            raise CurlParseError(f"Curl file '{path}' is not valid UTF-8 text.")
        return cls.parse(text)

    # -- Request building ---------------------------------------------------

    @property
    def user_agent(self) -> Optional[str]:
        for name, val in self.headers:
            if name.lower() == 'user-agent':
                return val
        return None

    def in_scope(self, url: str) -> bool:
        """Return True if credential headers may be sent to this URL."""
        host = urlparse(url).hostname
        return bool(self.scope_host and host and host.lower() == self.scope_host.lower())

    def headers_for(self, url: str) -> Dict[str, str]:
        """
        Headers to send for a request to url (User-Agent excluded; it is
        resolved globally so that --user-agent can override it).
        """
        excluded = {'user-agent'}
        if not self.in_scope(url):
            excluded |= self.SENSITIVE_HEADERS
        return {name: val for name, val in self.headers if name.lower() not in excluded}

    def open(self, request: urllib.request.Request, timeout: int):
        """Open a request, stripping credential headers on cross-host redirects."""
        if self._opener is None:
            self._opener = urllib.request.build_opener(_ScopedRedirectHandler(self))
        return self._opener.open(request, timeout=timeout)


class _ScopedRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Redirect handler that drops credential headers when leaving the source host."""

    def __init__(self, profile: CurlProfile):
        super().__init__()
        self.profile = profile

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and not self.profile.in_scope(newurl):
            for name in list(new.headers):
                if name.lower() in CurlProfile.SENSITIVE_HEADERS:
                    del new.headers[name]
            for name in list(new.unredirected_hdrs):
                if name.lower() in CurlProfile.SENSITIVE_HEADERS:
                    del new.unredirected_hdrs[name]
        return new


CURL_PROFILE: Optional[CurlProfile] = None


def build_request_headers(url: str) -> Dict[str, str]:
    """
    Build the HTTP headers for a scraping request.

    Without --curl-file this is just the User-Agent. With it, the browser
    headers are replayed, credentials only to the host they came from.
    """
    headers = CURL_PROFILE.headers_for(url) if CURL_PROFILE else {}
    headers['User-Agent'] = USER_AGENT
    return headers


def open_url(request: urllib.request.Request, timeout: int):
    """Open a scraping request, honouring --curl-file redirect scoping."""
    if CURL_PROFILE is not None:
        return CURL_PROFILE.open(request, timeout)
    return urllib.request.urlopen(request, timeout=timeout)


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
        self.extensions = {ext.lstrip('.').lower() for ext in extensions if ext.strip()}
        if not self.extensions:
            self.extensions = {ext.lower() for ext in EXTENSIONS}
        self.css_js_pattern = re.compile(r"\.(css|js)($|\?|#)")

    def fetch_links_from_url(self, url: str, timeout: int = DEFAULT_HTTP_TIMEOUT) -> Tuple[str, List[str]]:
        """
        Fetch all links from a given URL.

        Args:
            url: The URL to fetch links from
            timeout: Request timeout in seconds

        Returns:
            Tuple of (effective URL after redirects, links found on the page).
            The effective URL must be used as the base for resolving relative
            links, since e.g. GitHub Pages 301-redirects '/repo' to '/repo/'.
        """
        try:
            request = urllib.request.Request(url, headers=build_request_headers(url))
            with open_url(request, timeout) as response:
                # Final URL after any redirects; relative links resolve against it.
                effective_url = response.geturl() or url

                content_type = response.headers.get('Content-Type', '').split(';')[0]
                if 'text' not in content_type and 'application' not in content_type:
                    return effective_url, []

                raw_data = response.read()

                try:
                    data = raw_data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        data = raw_data.decode('latin-1')
                    except UnicodeDecodeError:
                        Logger.warning(f"Unable to decode content from {url}")
                        return effective_url, []

                parser = LinkParser()
                parser.feed(data)
                filtered_links = []
                for link in parser.links:
                    if link.startswith(('javascript:', 'mailto:', 'tel:', 'ftp:', 'data:')):
                        continue
                    if self.css_js_pattern.search(link):
                        continue
                    if not link or link.strip() == '':
                        continue
                    filtered_links.append(link)
                return effective_url, filtered_links

        except urllib.error.URLError as e:
            if url.startswith("mailto:"):
                Logger.info(f"Found mailto link {url}")
            else:
                Logger.error(f"Unable to open {url} Reason: {e}")
            return url, []
        except urllib.error.HTTPError as e:
            Logger.error(f"HTTP Error for URL {url} Reason: {e.code} - {e.reason}")
            return url, []
        except Exception as e:
            Logger.error(f"Unexpected error fetching {url} Reason: {e}")
            return url, []

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

        extension = os.path.splitext(path)[1].lstrip('.').lower()
        return extension in self.extensions


class FileDownloader:
    """Handles file downloading operations."""

    @staticmethod
    def calculate_hash(data: bytes) -> str:
        """
        Calculate the CRC32 checksum of the given data.

        Args:
            data: The binary content of the data to be hashed

        Returns:
            The hexadecimal CRC32 checksum (8 chars)
        """
        return f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"

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
            os.makedirs(download_dir, exist_ok=True)

            encoded_url = quote(url, safe=":/?&=")
            parsed_path = urlparse(encoded_url).path
            filename = os.path.basename(parsed_path)

            if not filename:
                filename = "downloaded_file"

            local_filename = os.path.join(download_dir, filename)

            request = urllib.request.Request(encoded_url, headers=build_request_headers(encoded_url))
            with open_url(request, timeout) as response:
                data = response.read()
                file_hash = FileDownloader.calculate_hash(data)

                if os.path.exists(local_filename):
                    with open(local_filename, 'rb') as existing_file:
                        existing_file_hash = FileDownloader.calculate_hash(existing_file.read())

                    if file_hash == existing_file_hash:
                        Logger.warning(f"Duplicate file detected for '{local_filename}'. Both have the same CRC32: {file_hash}.")
                        return
                    else:
                        new_local_filename = FileDownloader.find_unique_filename(local_filename)
                        Logger.info(f"File '{local_filename}' already exists with a different CRC32. Saving the new file as '{new_local_filename}'.")
                        local_filename = new_local_filename

                with open(local_filename, 'wb') as out_file:
                    out_file.write(data)
                Logger.info(f"Downloaded {url} to {local_filename}. CRC32: {file_hash}.")
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

        base_url, links = self.scraper.fetch_links_from_url(task.url)

        file_links = []
        for link in links:
            if self.scraper.is_valid_file_link(link):
                absolute_url = urljoin(base_url, link)
                file_links.append(absolute_url)

        if self.download_dir and not self.scan:
            for file_link in file_links:
                FileDownloader.download_file(file_link, self.download_dir)
        elif self.scan:
            for file_link in file_links:
                file_name = os.path.basename(urlparse(file_link).path)
                extension = os.path.splitext(file_name)[-1].lstrip('.').lower()  # Normalize to lowercase
                if extension:
                    self.file_stats.add_file(extension, file_link, file_name)

        if task.depth > 0:
            for link in links:
                if self.scraper.is_valid_file_link(link):
                    continue

                # Skip non-HTTP/HTTPS URLs (tel:, mailto:, javascript:, etc.)
                if not link.startswith(('http://', 'https://', '/')):
                    continue

                absolute_link = urljoin(base_url, link)
                parsed_link = urlparse(absolute_link)

                # Validate that it's an HTTP/HTTPS URL
                if parsed_link.scheme not in ('http', 'https'):
                    continue

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
                if task is None:
                    self.task_queue.task_done()
                    break

                if not isinstance(task, ScrapingTask):
                    self.task_queue.task_done()
                    continue

                if task.url in self.processed_urls:
                    self.task_queue.task_done()
                    continue

                if self.processed_urls.add(task.url):
                    try:
                        self.url_processor.process_url(task, self.task_queue)
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        self.errors += 1
                        Logger.error(f"Worker {self.worker_id} - Exception processing {task.url}: {e}")

                self.task_queue.task_done()
            except Exception as e:
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
        self.task_queue.put(self.initial_task)

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
            self.task_queue.join()
        except KeyboardInterrupt:
            Logger.warning("\nInterrupted by user. Stopping workers...")
            self.stop_event.set()

            for _ in range(self.num_threads):
                try:
                    self.task_queue.put_nowait(None)
                except queue.Full:
                    pass

            for worker in self.workers:
                worker.join(timeout=DEFAULT_SHUTDOWN_TIMEOUT)
                if worker.is_alive():
                    Logger.warning(f"Worker {worker.name} did not terminate gracefully")
            raise

        self.stop_event.set()

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
    def _safe_gps_links(lat: str, lon: str, address: str) -> Dict[str, str]:
        """
        Build HTML-safe anchor tags for the 'Address' and 'Map Link' fields.

        Text nodes are HTML-escaped and URLs are percent-encoded so that
        attacker-controlled metadata (e.g. a crafted Nominatim display_name)
        cannot inject markup into the report.

        Args:
            lat: Latitude (already formatted by MetaDetective)
            lon: Longitude (already formatted by MetaDetective)
            address: Resolved address text (may be empty)

        Returns:
            Mapping of field name -> safe HTML snippet
        """
        links: Dict[str, str] = {}
        lat_q = quote(str(lat), safe="")
        lon_q = quote(str(lon), safe="")
        map_url = f"https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat_q}&lon={lon_q}"
        links["Map Link"] = (
            f'<a href="{html.escape(map_url, quote=True)}" target="_blank" '
            f'rel="noopener noreferrer">View on Map</a>'
        )
        if address:
            search_url = NOMINATIM_SEARCH_URL + quote(address, safe="")
            links["Address"] = (
                f'<a href="{html.escape(search_url, quote=True)}" target="_blank" '
                f'rel="noopener noreferrer">{html.escape(address)}</a>'
            )
        return links

    @staticmethod
    def _render_singular_value(field: str, value: str) -> str:
        """
        Render a single (unique) metadata value as safe HTML.

        Every value is HTML-escaped. 'Map Link' values hold a plain URL and are
        wrapped in a safe anchor.

        Args:
            field: Metadata field name
            value: Value to render

        Returns:
            Safe HTML snippet
        """
        if field == "Map Link":
            return (
                f'<a href="{html.escape(value, quote=True)}" target="_blank" '
                f'rel="noopener noreferrer">View on Map</a>'
            )
        return html.escape(value)

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
        total_files = len(all_metadata)
        total_fields = sum(
            1 for m in all_metadata for f, v in m.items()
            if f in FIELDS and v and not PatternMatcher.matches_any_pattern(v, ignore_patterns)
        )
        unique_identities = set()
        for m in all_metadata:
            for field in ("Creator", "Author", "Last Modified By"):
                val = m.get(field)
                if val and not PatternMatcher.matches_any_pattern(val, ignore_patterns):
                    unique_identities.add(val)

        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'<title>MetaDetective {__version__} - Export Report</title>',
            CSS_STYLE,
            '</head>',
            '<body>',
            '<div class="report-wrap">',
            '<div class="header">',
            '<h1>Meta<span>Detective</span></h1>',
            f'<div class="sub">Export Report - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
            '</div>',
            '<div class="stats">',
            f'<div class="stat"><div class="stat-val">{total_files}</div><div class="stat-label">Files</div></div>',
            f'<div class="stat"><div class="stat-val">{total_fields}</div><div class="stat-label">Fields</div></div>',
            f'<div class="stat"><div class="stat-val">{len(unique_identities)}</div><div class="stat-label">Identities</div></div>',
            '</div>',
        ]

        if args.display == "all":
            for metadata in all_metadata:
                html_parts.append('<div class="metadata-entry">')

                gps_html: Dict[str, str] = {}
                formatted_gps = metadata.get("Formatted GPS Position")
                if formatted_gps:
                    try:
                        lat, lon = formatted_gps.split(", ")
                        address = AddressResolver.get_address_from_coords(lat, lon)
                        if address:
                            metadata["Address"] = address
                        metadata["Map Link"] = "View on Map"
                        gps_html = MetadataExporter._safe_gps_links(lat, lon, address)
                    except ValueError:
                        pass

                displayed_fields = 0
                for field, value in metadata.items():
                    if field in FIELDS and value and not PatternMatcher.matches_any_pattern(value, ignore_patterns):
                        rendered = gps_html.get(field, html.escape(value))
                        html_parts.append(
                            f'<div class="field-row"><span class="field-key">{html.escape(field)}</span>'
                            f'<span class="field-val">{rendered}</span></div>'
                        )
                        displayed_fields += 1

                if displayed_fields == 0:
                    html_parts.append('<p>No relevant metadata found.</p>')

                html_parts.append('</div>')
        elif args.display == "singular":
            unique_values = defaultdict(set)

            for metadata in all_metadata:
                formatted_gps = metadata.get("Formatted GPS Position")
                if formatted_gps:
                    try:
                        lat, lon = formatted_gps.split(", ")
                        # 'Address' is not part of UNIQUE_FIELDS, so it is never
                        # displayed in singular mode: skip the Nominatim lookup
                        # entirely (no wasted request, no coordinate leak).
                        metadata["Map Link"] = NOMINATIM_LINK.format(lat=lat, lon=lon)
                    except ValueError:
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
                    html_parts.append(f'<h3>{html.escape(field)}</h3>')
                    if args.format == 'formatted':
                        html_parts.append('<ul>')
                        for unique_value in unique_cased_values:
                            html_parts.append(f'<li>{MetadataExporter._render_singular_value(field, unique_value)}</li>')
                        html_parts.append('</ul>')
                    else:
                        rendered = ', '.join(
                            MetadataExporter._render_singular_value(field, v)
                            for v in unique_cased_values
                        )
                        html_parts.append(f"<p>{rendered}</p>")

        html_parts.append(f'<div class="footer">MetaDetective {__version__}</div>')
        html_parts.append('</div></body></html>')
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

    @staticmethod
    def export_metadata_to_json(
        args: Namespace,
        all_metadata: List[Dict[str, Any]],
        ignore_patterns: List[str]
    ) -> str:
        """
        Export the provided metadata to JSON format.

        Args:
            args: Arguments specifying the display method and other options
            all_metadata: A list of metadata entries to export
            ignore_patterns: A list of patterns to ignore during the export

        Returns:
            JSON string representation of the metadata
        """
        output: Dict[str, Any] = {
            "tool": f"MetaDetective {__version__}",
            "generated": datetime.datetime.now().isoformat(),
        }

        if args.display == "all":
            entries = []
            for metadata in all_metadata:
                AddressResolver.format_gps_data(metadata)
                entry = {
                    field: value
                    for field, value in metadata.items()
                    if field in FIELDS and value and not PatternMatcher.matches_any_pattern(value, ignore_patterns)
                }
                if entry:
                    entries.append(entry)
            output["files"] = entries

        elif args.display == "singular":
            unique_values: Dict[str, Any] = defaultdict(set)
            for metadata in all_metadata:
                AddressResolver.format_gps_data(metadata)
                for field in UNIQUE_FIELDS:
                    value = metadata.get(field)
                    if field == "Hyperlinks" and value:
                        links = [link.strip() for link in value.split(',')]
                        valid_links = [
                            link for link in links
                            if not PatternMatcher.matches_any_pattern(link, ignore_patterns)
                        ]
                        for link in valid_links:
                            unique_values[field].add(link)
                    elif value and not PatternMatcher.matches_any_pattern(value, ignore_patterns):
                        unique_values[field].add(value)

            output["unique"] = {
                field: sorted(values)
                for field, values in unique_values.items()
            }

        return json.dumps(output, indent=2, ensure_ascii=False)


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
    Validate that a directory path exists (for input directories).

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


def valid_output_directory(path: str) -> str:
    """
    Validate or create an output directory path.

    If the directory does not exist, it is created automatically.

    Args:
        path: The directory path for output

    Returns:
        The valid directory path

    Raises:
        argparse.ArgumentTypeError: If the path exists but is not a directory,
            or if directory creation fails.
    """
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise argparse.ArgumentTypeError(f"Path '{path}' exists but is not a directory.")
        return path

    try:
        os.makedirs(path, exist_ok=True)
        return path
    except OSError as exc:
        raise argparse.ArgumentTypeError(f"Cannot create directory '{path}': {exc}")


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


def looks_like_url(value: str) -> bool:
    """
    Return True if the value looks like an http(s) URL.

    Args:
        value: The string to test

    Returns:
        True if the value starts with http:// or https://
    """
    return bool(re.match(r'^https?://', value, re.IGNORECASE))


def resolve_positional_target(parser: argparse.ArgumentParser, args: Namespace) -> None:
    """
    Resolve the positional TARGET into an explicit mode.

    A http(s):// URL enables scraping mode; an existing directory or file
    enables analysis mode. Incompatible combinations raise a parser error so
    that safeguards (no web scan on a local path, no analysis flags on a URL)
    are preserved.

    Args:
        parser: The argument parser, used for consistent error reporting
        args: Parsed arguments (modified in-place)
    """
    target = args.target

    if looks_like_url(target):
        if args.directory or args.files or args.type != ['all'] or args.ignore:
            parser.error(
                "A URL target enables scraping mode and cannot be combined with analysis "
                "options (-d/--directory, -f/--files, -t/--type, -i/--ignore)."
            )
        if args.url and args.url != target:
            parser.error("Conflicting URLs provided as positional target and --url.")
        try:
            valid_url(target)
        except argparse.ArgumentTypeError as exc:
            parser.error(str(exc))
        args.scraping = True
        args.url = target
    else:
        if args.scraping or args.url or args.scan or args.download_dir:
            parser.error(
                "A directory/file target enables analysis mode and cannot be combined with "
                "scraping options (-s/--scraping, -u/--url, --scan, --download-dir)."
            )
        if args.directory or args.files:
            parser.error("Do not combine a positional target with -d/--directory or -f/--files.")
        if os.path.isdir(target):
            args.directory = target
        elif os.path.isfile(target):
            args.files = [target]
        else:
            parser.error(f"Target '{target}' is not a URL, an existing directory, or an existing file.")


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


def display_summary(all_metadata: List[Dict[str, Any]], ignore_patterns: List[str]) -> None:
    """
    Print a concise statistical summary of extracted metadata.

    Shows: file count, unique identities (Author/Creator/Last Modified By),
    unique emails, files with GPS, unique tools, date range.
    """
    total = len(all_metadata)

    identities: Set[str] = set()
    emails: Set[str] = set()
    tools: Set[str] = set()
    gps_count = 0
    dates: List[str] = []

    for m in all_metadata:
        for field in ("Creator", "Author", "Last Modified By"):
            val = m.get(field)
            if val and not PatternMatcher.matches_any_pattern(val, ignore_patterns):
                identities.add(val)

        hyperlinks = m.get("Hyperlinks", "")
        if hyperlinks:
            for link in hyperlinks.split(","):
                link = link.strip()
                if "@" in link and not PatternMatcher.matches_any_pattern(link, ignore_patterns):
                    emails.add(link)

        for field in ("Creator Tool", "Producer", "Software"):
            val = m.get(field)
            if val and not PatternMatcher.matches_any_pattern(val, ignore_patterns):
                tools.add(val)

        if m.get("GPS Position") or m.get("Formatted GPS Position"):
            gps_count += 1

        for field in ("Create Date", "Modify Date"):
            val = m.get(field)
            if val:
                dates.append(val)

    print("\n" + "=" * 50)
    print("  SUMMARY")
    print("=" * 50)
    print(f"  Files analyzed    : {total}")
    print(f"  Unique identities : {len(identities)}")
    if identities:
        for name in sorted(identities):
            print(f"    > {name}")
    print(f"  Emails found      : {len(emails)}")
    if emails:
        for email in sorted(emails):
            print(f"    > {email}")
    print(f"  Files with GPS    : {gps_count}")
    print(f"  Unique tools      : {len(tools)}")
    if tools:
        for tool in sorted(tools):
            print(f"    > {tool}")
    if dates:
        dates_sorted = sorted(dates)
        print(f"  Date range        : {dates_sorted[0]} -> {dates_sorted[-1]}")
    print("=" * 50 + "\n")


def display_timeline(all_metadata: List[Dict[str, Any]], ignore_patterns: List[str]) -> None:
    """
    Display metadata entries sorted chronologically.

    Shows a timeline of document creation and modification with
    author/creator attribution.
    """
    events: List[Tuple[str, str, str, str]] = []

    for m in all_metadata:
        filename = m.get("File Name", "unknown")
        author = m.get("Creator") or m.get("Author") or m.get("Last Modified By") or "unknown"
        tool = m.get("Creator Tool") or m.get("Producer") or m.get("Software") or ""

        create_date = m.get("Create Date")
        if create_date and not PatternMatcher.matches_any_pattern(create_date, ignore_patterns):
            events.append((create_date, "CREATED", filename, f"{author} ({tool})" if tool else author))

        modify_date = m.get("Modify Date")
        if modify_date and not PatternMatcher.matches_any_pattern(modify_date, ignore_patterns):
            events.append((modify_date, "MODIFIED", filename, f"{author} ({tool})" if tool else author))

    if not events:
        print("\nNo date metadata found for timeline.")
        return

    events.sort(key=lambda x: x[0])

    print("\n" + "=" * 70)
    print("  TIMELINE")
    print("=" * 70)

    current_date = ""
    for date_str, action, filename, who in events:
        day = date_str[:10] if len(date_str) >= 10 else date_str
        if day != current_date:
            current_date = day
            print(f"\n  [{day}]")
        action_marker = "+" if action == "CREATED" else "~"
        print(f"    {action_marker} {date_str:25s} {action:8s}  {filename}")
        print(f"      by {who}")

    print("\n" + "=" * 70)
    print(f"  {len(events)} event(s) across {len(set(e[0][:10] for e in events if len(e[0]) >= 10))} day(s)")
    print("=" * 70 + "\n")


def main():
    """Main entry point for the application."""
    if '--no-banner' not in sys.argv:
        show_banner()
    check_exiftool_installed()

    parser = argparse.ArgumentParser(
        description="Retrieve and display metadata from files using exiftool.",
        epilog="Example commands:\n\n"
               "# Quick shortcuts (positional target, auto-detected):\n"
               "python3 MetaDetective.py ./loot/                      # analyze a directory\n"
               "python3 MetaDetective.py report.pdf                   # analyze a single file\n"
               "python3 MetaDetective.py https://target.com/ --scan   # scrape a site\n"
               "\n"
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
               "python3 MetaDetective.py --scraping --depth 1 --download-dir directory --url https://example.com/\n\n"
               "   # Scrape a bot-protected site with headers copied from your browser ('Copy as cURL'):\n"
               "python3 MetaDetective.py --scraping --scan --curl-file request.txt --url https://example.com/\n",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        'target', nargs='?', metavar='TARGET',
        help="Positional shortcut, auto-detected:\n"
             "  - a directory or file  -> analysis mode (like -d / -f)\n"
             "  - an http(s):// URL    -> scraping mode (like -s -u)"
    )

    scraping_group = parser.add_argument_group('scraping options', 'Options for scraping files containing potential metadata from a website.')
    scraping_group.add_argument('-s', '--scraping', action='store_true', help="Argument required to activate scraping mode.")
    scraping_group.add_argument('-u', "--url", type=valid_url, help="Site url for scraping.")
    scraping_group.add_argument("--scan", action="store_true", help="Scans the website and displays information and statistics without downloading files.")
    scraping_group.add_argument('--extensions', nargs='+', type=str.lower, help='File extensions to filter by, e.g., --extensions pdf jpg png')
    scraping_group.add_argument("--depth", type=int, default=DEFAULT_DEPTH, help=f"Depth of links to follow on the site (default: {DEFAULT_DEPTH}).")
    scraping_group.add_argument("--download-dir", type=valid_output_directory, help=f"Directory to store scraped files (created if missing). Defaults to ./{DEFAULT_DOWNLOAD_DIR}/ when neither --scan nor --download-dir is given.")
    scraping_group.add_argument("--follow-extern", action="store_true", help="Follow external links.")
    scraping_group.add_argument("--threads", type=int, default=DEFAULT_NUM_THREADS, help="Number of threads to use (1-100).")
    scraping_group.add_argument("--rate", type=int, default=DEFAULT_RATE_LIMIT, help="Maximum number of requests per second (0.1-1000).")
    ua_presets_list = ", ".join(UA_PRESETS.keys())
    scraping_group.add_argument(
        "--user-agent", metavar="UA",
        help=f"Custom User-Agent string or preset name. Presets: {ua_presets_list}. "
             "Example: --user-agent stealth, --user-agent chrome-win, "
             "or --user-agent 'MetaDetective/2.0'"
    )
    scraping_group.add_argument(
        "--curl-file", metavar="FILE",
        help="Replay a real browser's request headers to get past bot detection.\n"
             "FILE holds a request copied with the browser dev tools 'Copy as cURL'\n"
             "(bash or cmd); use '-' to read it from stdin. All headers are reused;\n"
             "cookies and auth headers are only sent to the host it was copied from.\n"
             "--user-agent, if also given, overrides the imported User-Agent."
    )

    analysis_group = parser.add_argument_group('analysis options', 'Main analysis options.')
    analysis_group.add_argument('-d', '--directory', type=valid_directory, help="Directory containing the files to be analyzed.")
    analysis_group.add_argument('-f', '--files', nargs='+', help="File or space-separated list of files to be analyzed.")
    analysis_group.add_argument('-t', '--type', nargs='+', default=['all'], help="File types (extensions) to be analyzed (all by default).")

    display_group = parser.add_argument_group('display options', 'Options for displaying results.')
    display_group.add_argument('-i', '--ignore', nargs='+', help="Ignore one or more results separated by spaces for keywords or regexes.")
    display_group.add_argument('--parse-only', nargs='+', metavar='FIELD', help="Only extract and display specified fields (e.g. Author Creator 'Last Modified By').")
    display_group.add_argument('--display', choices=['all', 'singular'], default='singular', help="Display options:\n'all' to display all relevant results for each file one by one.\n'singular' to display condensed results.'")
    display_group.add_argument('--format', choices=['formatted', 'concise'], help="Display format ('singular' display required):\n'formatted' for a formatted (stylized) display.\n'concise' for more classic (basic) formatting.")
    display_group.add_argument('--summary', action='store_true', help="Show a statistical summary: file count, unique identities, emails, GPS exposure, tools, date range.")
    display_group.add_argument('--timeline', action='store_true', help="Display a chronological timeline of document creation and modification events.")
    display_group.add_argument('--no-banner', action='store_true', help="Suppress the ASCII banner. Useful for scripting and pipeline integration.")
    display_group.add_argument('--no-geocode', action='store_true', help="Disable GPS reverse geocoding. No coordinates are sent to Nominatim/OpenStreetMap; raw GPS values are still shown.")
    display_group.add_argument('--nominatim-url', metavar='URL', help="Base URL of a Nominatim reverse-geocoding server (e.g. https://nominatim.example.com). Default: public OpenStreetMap server.")

    export_group = parser.add_argument_group('export options', 'Options for exporting results.')
    export_group.add_argument('-e', '--export', nargs='?', const='html', choices=['html', 'txt', 'json'], default=None, help="Export results. Default format is HTML. Text (txt) and JSON (json) exports are also possible.")
    export_group.add_argument('-c', '--custom', type=valid_filename, help="Custom file name. The name is generated with default values, but you can add a suffix.")
    export_group.add_argument('-o', '--out', type=valid_output_directory, default=os.getcwd(), help="Specify file export directory. Created automatically if it does not exist.")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # Resolve the positional TARGET (URL -> scraping, directory/file -> analysis).
    if args.target is not None:
        resolve_positional_target(parser, args)

    # Reverse-geocoding configuration (analysis / export only).
    global GEOCODE_ENABLED, NOMINATIM_HOST, NOMINATIM_SCHEME
    if args.no_geocode:
        GEOCODE_ENABLED = False
    if args.nominatim_url:
        parsed_nominatim = urlparse(args.nominatim_url)
        if parsed_nominatim.scheme not in ('http', 'https') or not parsed_nominatim.netloc:
            parser.error("--nominatim-url must be a full http(s):// URL, e.g. https://nominatim.example.com")
        NOMINATIM_SCHEME = parsed_nominatim.scheme
        NOMINATIM_HOST = parsed_nominatim.netloc

    if args.curl_file and not args.scraping:
        parser.error("--curl-file only applies to scraping mode (--scraping/-s or a URL target).")

    if args.scraping:
        if args.directory or args.files or args.ignore:
            parser.error("Analysis arguments (--directory/-d, --files/-f, and --ignore/-i) cannot be used with scrapping options (--scraping/-s).")

        if args.scan and args.download_dir:
            parser.error("The scan (--scan) and download (--download-dir) arguments cannot be specified together. Choose one or the other in scraping mode, but not both.")
        elif not args.scan and not args.download_dir:
            # No mode chosen: default to download mode into ./loot/ (created if missing).
            try:
                args.download_dir = valid_output_directory(DEFAULT_DOWNLOAD_DIR)
            except argparse.ArgumentTypeError as exc:
                parser.error(str(exc))
            if '--no-banner' not in sys.argv:
                print(f"[*] No --scan/--download-dir given: downloading to default './{DEFAULT_DOWNLOAD_DIR}/'.")

        if not args.url:
            parser.error("The url choice argument (-u or --url) is required for scraping mode.")

        extensions = args.extensions if args.extensions else EXTENSIONS.copy()

        global USER_AGENT, CURL_PROFILE
        if args.curl_file:
            try:
                CURL_PROFILE = CurlProfile.from_file(args.curl_file)
            except CurlParseError as exc:
                parser.error(f"--curl-file: {exc}")
            if CURL_PROFILE.scope_host is None:
                CURL_PROFILE.scope_host = urlparse(args.url).hostname
                Logger.warning("--curl-file: no URL found in the curl command; cookies and auth headers will be scoped to the --url host.")
            elif not CURL_PROFILE.in_scope(args.url):
                Logger.warning(f"--curl-file: command was copied from '{CURL_PROFILE.scope_host}' but scraping '{urlparse(args.url).hostname}'; cookies and auth headers will only be sent to '{CURL_PROFILE.scope_host}'.")
            if CURL_PROFILE.user_agent and not args.user_agent:
                USER_AGENT = CURL_PROFILE.user_agent
            print(f"[*] Imported {len(CURL_PROFILE.headers)} header(s) from curl file for {CURL_PROFILE.scope_host}")

        if args.user_agent:
            ua = args.user_agent
            if ua in UA_PRESETS:
                USER_AGENT = UA_PRESETS[ua]
                print(f"[*] User-Agent preset: {ua}")
            else:
                USER_AGENT = ua
                print(f"[*] User-Agent custom: {ua[:60]}...")

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

        if args.no_geocode and '--no-banner' not in sys.argv:
            print("[*] Reverse geocoding disabled (--no-geocode): GPS coordinates are not sent to Nominatim.")

        if args.display == 'all' and args.format:
            parser.error("The formatting (--format) argument is not compatible with the 'all' display mode (--display all).")

        if args.display == 'singular' and args.format is None:
            args.format = 'concise'

        if args.parse_only:
            requested = {f.lower() for f in args.parse_only}
            active_fields = [f for f in FIELDS if f.lower() in requested]
            unknown = requested - {f.lower() for f in FIELDS}
            if unknown:
                Logger.warning(f"Unknown fields ignored: {', '.join(unknown)}. Available: {', '.join(FIELDS)}")
            if not active_fields:
                parser.error("No valid fields specified with --parse-only.")
        else:
            active_fields = FIELDS

        files = FileOperations.get_files(args)
        all_metadata = [MetadataExtractor.get_metadata(file, active_fields) for file in files]

        if args.summary:
            display_summary(all_metadata, ignore_patterns)

        if args.timeline:
            display_timeline(all_metadata, ignore_patterns)

        if args.export:
            if args.export == 'html':
                content = MetadataExporter.export_metadata_to_html(args, all_metadata, ignore_patterns)
                file_extension = '.html'
            elif args.export == 'json':
                content = MetadataExporter.export_metadata_to_json(args, all_metadata, ignore_patterns)
                file_extension = '.json'
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
