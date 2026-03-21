<div id="top" align="center">

<!-- Sponsorship -->
<p align="center">
  <a href="https://iproyal.com/?r=848799" target="_blank">
    <img src="https://raw.githubusercontent.com/franckferman/MetaDetective/stable/docs/github/graphical_resources/IPRoyal-Logo_Transparent_500x500.png" alt="Sponsored by IPRoyal" width="180">
  </a>
</p>
<p align="center"><b>Supported by <a href="https://iproyal.com/?r=848799">IPRoyal</a></b> &mdash; Proxy services for OSINT and security research.</p>

<br>

[![Contributors][contributors-shield]](https://github.com/franckferman/MetaDetective/graphs/contributors)
[![Forks][forks-shield]](https://github.com/franckferman/MetaDetective/network/members)
[![Stargazers][stars-shield]](https://github.com/franckferman/MetaDetective/stargazers)
[![Issues][issues-shield]](https://github.com/franckferman/MetaDetective/issues)
[![License][license-shield]](https://github.com/franckferman/MetaDetective/blob/stable/LICENSE)

<a href="https://github.com/franckferman/MetaDetective">
  <img src="https://raw.githubusercontent.com/franckferman/MetaDetective/stable/docs/github/graphical_resources/Logo-Without_background-MetaDetective.png" alt="MetaDetective" width="340">
</a>

<h3 align="center">MetaDetective</h3>
<p align="center">Metadata extraction and web scraping for OSINT and pentesting.</p>

<p align="center">
  <a href="https://asciinema.org/a/55mEbe7GFVfIJ6OSfjOaDeYLv">Demo</a>
  &nbsp;&middot;&nbsp;
  <a href="https://github.com/franckferman/MetaDetective/issues">Report a bug</a>
  &nbsp;&middot;&nbsp;
  <a href="https://github.com/franckferman/MetaDetective/issues">Request a feature</a>
</p>

</div>

---

## Table of Contents

- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## About

MetaDetective is a single-file Python 3 tool for metadata extraction and web scraping, built for OSINT and pentesting workflows.

It has no Python dependencies beyond exiftool. One `curl` and you're operational.

**What it extracts:** authors, software versions, GPS coordinates, creation/modification dates, internal hostnames, serial numbers, hyperlinks, camera models - across documents, images, and email files.

**What it does beyond extraction:**
- Direct web scraping of target sites (no search engine dependency, no IP blocks)
- GPS reverse geocoding with OpenStreetMap, map link generation
- Export to HTML, TXT, or JSON
- Selective field extraction with `--parse-only`
- Deduplication across multiple files

It was built as a replacement for Metagoofil, which dropped native metadata analysis and relied on Google search (rate limiting, CAPTCHAs, proxy overhead).

<p align="center">
  <img src="https://raw.githubusercontent.com/franckferman/MetaDetective/stable/docs/github/graphical_resources/Screenshot-MetaDetective_Demo.png" alt="MetaDetective demo" width="700">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/franckferman/MetaDetective/stable/docs/github/graphical_resources/Screenshot-MetaDetective_Scraping_Demo.png" alt="MetaDetective scraping demo" width="700">
</p>

---

## Installation

**Requirements:** Python 3, exiftool.

```bash
# Debian / Ubuntu / Kali
sudo apt install libimage-exiftool-perl

# macOS
brew install exiftool
```

### Direct download (recommended for field use)

```bash
curl -O https://raw.githubusercontent.com/franckferman/MetaDetective/stable/src/MetaDetective/MetaDetective.py
python3 MetaDetective.py -h
```

### pip

```bash
pip install MetaDetective
metadetective -h
```

### git clone

```bash
git clone https://github.com/franckferman/MetaDetective.git
cd MetaDetective
python3 src/MetaDetective/MetaDetective.py -h
```

### Docker

```bash
docker pull franckferman/metadetective
docker run --rm franckferman/metadetective -h

# Mount a local directory
docker run --rm -v $(pwd)/loot:/data franckferman/metadetective -d /data
```

---

## Usage

### File analysis

```bash
# Analyze a directory (deduplicated singular view by default)
python3 MetaDetective.py -d ./loot/

# Specific file types, filter noise
python3 MetaDetective.py -d ./loot/ -t pdf docx -i admin anonymous

# Per-file display with formatted output
python3 MetaDetective.py -d ./loot/ --display all --format formatted

# Single file
python3 MetaDetective.py -f report.pdf

# Multiple files
python3 MetaDetective.py -f report.pdf photo.heic
```

### Selective parsing

`--parse-only` limits extraction to specific fields. Useful to cut noise or target a specific data point.

```bash
# Extract only Author and Creator fields
python3 MetaDetective.py -d ./loot/ --parse-only Author Creator

# Extract GPS data only from iPhone photos
python3 MetaDetective.py -d ./photos/ -t heic heif --parse-only 'GPS Position' 'Map Link'
```

### Export

```bash
# HTML report (default)
python3 MetaDetective.py -d ./loot/ -e

# TXT
python3 MetaDetective.py -d ./loot/ -e txt

# JSON - singular (deduplicated values per field)
python3 MetaDetective.py -d ./loot/ -e json

# JSON - per file
python3 MetaDetective.py -d ./loot/ --display all -e json

# Custom filename suffix and output directory
python3 MetaDetective.py -d ./loot/ -e json -c pentest-corp -o ~/results/
```

JSON singular output structure:
```json
{
  "tool": "MetaDetective",
  "generated": "2026-03-21T...",
  "unique": {
    "Author": ["Alice Martin", "Bob Dupont"],
    "Creator Tool": ["Microsoft Word 16.0"]
  }
}
```

Pivot with jq:
```bash
jq '.unique.Author' MetaDetective_Export-*.json
```

### Web scraping

```bash
# Scan target site, list files found
python3 MetaDetective.py --scraping --scan --url https://target.com/

# Filter by extension
python3 MetaDetective.py --scraping --scan --url https://target.com/ --extensions pdf docx xlsx

# Download files (depth 2, 8 threads)
python3 MetaDetective.py --scraping --url https://target.com/ \
  --download-dir ~/loot/ --extensions pdf docx --depth 2 --threads 8

# Control request rate (requests/sec)
python3 MetaDetective.py --scraping --url https://target.com/ \
  --download-dir ~/loot/ --rate 5

# Follow external links
python3 MetaDetective.py --scraping --url https://target.com/ \
  --download-dir ~/loot/ --follow-extern
```

### Filtering and display options

| Flag | Description |
|------|-------------|
| `-t pdf docx` | Restrict to file types |
| `-i admin anonymous` | Ignore values matching pattern (regex supported) |
| `--parse-only Author Creator` | Extract only specified fields |
| `--display all` | Show metadata per file |
| `--display singular` | Deduplicated view across all files (default) |
| `--format formatted` | Decorated output |
| `--format concise` | Compact output |

### Supported formats

Documents: PDF, DOCX, ODT, XLS, XLSX, PPTX, ODP, RTF, CSV, XML
Images: JPEG, PNG, TIFF, BMP, GIF, SVG, PSD, HEIC, HEIF
Email: EML, MSG, PST, OST
Video: MP4, MOV

---

## Contributing

Open an issue or submit a pull request on GitHub.

---

## License

AGPL-3.0. See [LICENSE](https://github.com/franckferman/MetaDetective/blob/stable/LICENSE).

MetaDetective is provided for educational and authorized security testing purposes. You are responsible for ensuring compliance with applicable laws.

---

## Star History

<a href="https://star-history.com/#franckferman/MetaDetective&Timeline">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=franckferman/MetaDetective&type=Timeline&theme=dark" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=franckferman/MetaDetective&type=Timeline" />
  </picture>
</a>

---

## Contact

[![ProtonMail][protonmail-shield]](mailto:contact@franckferman.fr)
[![LinkedIn][linkedin-shield]](https://www.linkedin.com/in/franckferman)
[![Twitter][twitter-shield]](https://www.twitter.com/franckferman)

<p align="right"><a href="#top">Back to top</a></p>

<!-- shields -->
[contributors-shield]: https://img.shields.io/github/contributors/franckferman/MetaDetective.svg?style=for-the-badge
[forks-shield]: https://img.shields.io/github/forks/franckferman/MetaDetective.svg?style=for-the-badge
[stars-shield]: https://img.shields.io/github/stars/franckferman/MetaDetective.svg?style=for-the-badge
[issues-shield]: https://img.shields.io/github/issues/franckferman/MetaDetective.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/franckferman/MetaDetective.svg?style=for-the-badge
[protonmail-shield]: https://img.shields.io/badge/ProtonMail-8B89CC?style=for-the-badge&logo=protonmail&logoColor=white
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=blue
[twitter-shield]: https://img.shields.io/badge/-Twitter-black.svg?style=for-the-badge&logo=twitter&colorB=blue
