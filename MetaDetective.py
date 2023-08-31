#!/usr/bin/env python3

"""Unleash Metadata Intelligence with MetaDetective. Your Assistant Beyond Metagoofil.

Created By  : Franck FERMAN @franckferman
Created Date: 27/08/2023
Version     : 1.0.0 (27/08/2023)
"""

import argparse
import os
import re
import subprocess
import sys
import webbrowser
from argparse import Namespace
from collections import defaultdict
from typing import List, Dict


BANNER = r"""
___  ___     _       ______     _            _   _
|  \/  |    | |      |  _  \   | |          | | (_)
| .  . | ___| |_ __ _| | | |___| |_ ___  ___| |_ ___   _____
| |\/| |/ _ \ __/ _` | | | / _ \ __/ _ \/ __| __| \ \ / / _ \
| |  | |  __/ || (_| | |/ /  __/ ||  __/ (__| |_| |\ V /  __/
\_|  |_/\___|\__\__,_|___/ \___|\__\___|\___|\__|_| \_/ \___|
"""
FIELDS = [
    "File Name", "Title", "Creator", "Author", "Last Modified By",
    "Hyperlinks", "Company", "Creator Tool", "Producer"
]
UNIQUE_FIELDS = [
    "Creator", "Author", "Last Modified By", "Hyperlinks", "Creator Tool", "Producer"
]
EXIFTOOL_NOT_INSTALLED = "Error: exiftool is not installed. Please install it to continue."
EXIFTOOL_EXECUTION_ERROR = "Error: exiftool encountered an error."


def show_banner():
    print(BANNER)


def check_exiftool_installed() -> None:
    """Verify exiftool installation and exit the program if absent or on execution error."""
    try:
        subprocess.run(["exiftool", "-ver"], capture_output=True, check=True, text=True)
    except FileNotFoundError:
        sys.exit(EXIFTOOL_NOT_INSTALLED)
    except subprocess.CalledProcessError:
        sys.exit(EXIFTOOL_EXECUTION_ERROR)


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
                metadata[key.strip()] = value.strip()

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
            for field, value in metadata.items():
                if not matches_any_pattern(value, ignore_patterns):
                    print(f"{field}: {value}")
            print("-" * 40)

    elif args.display == "singular":
        unique_values = defaultdict(set)

        for metadata in all_metadata:
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

            if args.format == 'formatted':
                print(f"{field}:")
                for unique_value in unique_cased_values:
                    print(f"    - {unique_value}")
            else:  # 'concise'
                print(f"{field}: {', '.join(unique_cased_values)}")
            print()


def open_browser(url: str, preferred_browsers: List[str] = ['chrome', 'chromium', 'firefox']) -> bool:
    """
    Opens the given URL in a preferred web browser.

    Args:
        url (str): The URL to open.
        preferred_browsers (List[str], optional): List of preferred browser names in order. Defaults to ['chrome', 'chromium', 'firefox'].

    Returns:
        bool: True if the URL was successfully opened, False otherwise.
    """
    for browser in preferred_browsers:
        try:
            webbrowser.get(browser).open(url)
            return True
        except webbrowser.Error:
            continue

    try:
        webbrowser.open(url)
        return True
    except webbrowser.Error:
        return False


def main():
    if '-APTX4869' in sys.argv:
        if open_browser('https://youtu.be/3gSN-LR0NTw'):
            sys.exit(0)
        else:
            print("Error: No suitable browser found to open the URL.")
        
    show_banner()
    check_exiftool_installed()

    parser = argparse.ArgumentParser(description="Retrieve and display metadata from files using exiftool.",
                                     epilog="Example commands:\n"
                                            "  python3 MetaDetective.py -d directory\n"
                                            "  python3 MetaDetective.py -d directory -i ^admin anonymous -t doc pdf\n"
                                            "  python3 MetaDetective.py -d directory -t all -display singular -format formatted\n",
                                    formatter_class=argparse.RawTextHelpFormatter
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--directory', help="Directory to analyze.")
    group.add_argument('-f', '--files', nargs='+', help="File or list of files to analyze.")

    parser.add_argument('-i', '--ignore', nargs='+', help="Ignore specific items in display using regex or words.")
    parser.add_argument('-t', '--type', nargs='+', default=['all'], help="File extension(s) or 'all' for all files.")
    parser.add_argument('-display', choices=['all', 'singular'],
                        default='singular', help="Display mode: 'all' or 'singular'")
    parser.add_argument('-format', choices=['formatted', 'concise'],
                        help="Display format for 'singular' mode: 'formatted' or 'concise'")

    args = parser.parse_args()

    ignore_patterns = args.ignore if args.ignore else []

    if args.display == 'all' and args.format is not None:
        print("Error: The -format argument is not allowed with -display all.")
        sys.exit(1)

    if args.display == 'singular' and args.format is None:
        args.format = 'concise'

    files = get_files(args)

    all_metadata = [get_metadata(file, FIELDS) for file in files]

    display_metadata(args, all_metadata, ignore_patterns)


if __name__ == "__main__":
    main()
