## TODO

### Metadata enhancements

- [X] ~~**GPS and photo metadata improvements**~~
  - [X] ~~Add missing metadata fields, especially for geolocation, camera model name, and other device-specific information for images.~~
  - [X] ~~Develop a function to convert GPS data to OSM or Google Maps links.~~
  - [X] ~~Add HEIC/HEIF support (iPhone/iPad photos with high-precision GPS data).~~

### Data export features

- [X] ~~**Support various export formats**~~
  - [X] ~~Added support for exporting data in HTML format.~~
  - [X] ~~Added support for exporting data in TXT format.~~
  - [X] ~~Added support for exporting data in JSON format.~~
  - [X] ~~Implement customizable export options for users.~~
  - [X] ~~Implement advanced customizable export options for users.~~

### GitHub Actions

- [X] ~~**PyPI Automatic Upload on Release**~~
  - [X] ~~Integrate GitHub Actions to trigger PyPI package upload on every new release.~~

### Performance Enhancements

- [X] ~~**Optimize File Comparison for Duplication Avoidance**~~
  - [X] ~~Replace SHA256 hash verification with CRC32 (zlib stdlib, 10-50x faster, sufficient for deduplication).~~

### Functionalities for Parsing

- [X] ~~**Selective field extraction**~~
  - [X] ~~Add --parse-only flag to limit extraction to specified fields only.~~

- [ ] **Advanced Parsing Features**
  - [ ] Include options for automatic modification and enrichment of data.
    - [ ] Develop feature to automatically append email aliases (domain names) to usernames.

### Advanced Filtering

- [ ] **Enhanced Filtering Capabilities**
  - [X] ~~Add support for scraping filter options.~~
  - [ ] Implement local filtering based on sections like "Author" and "Last Modified By".
    - [ ] Add --filter-field to filter entire file entries by field value (distinct from --ignore which filters values, and --parse-only which filters fields).

### Security (report hardening)

- [X] ~~**Escape all metadata values in the HTML export (stored-XSS fix)**~~
  - [X] ~~HTML-escape every metadata value/field; build Address/Map Link with escaped text and encoded URLs.~~
  - [X] ~~Add regression tests with `<img onerror>` / `<script>` payloads.~~
  - [ ] Add a Content-Security-Policy `<meta>` to the report as defense-in-depth.

### Geolocation / privacy

- [X] ~~**Opt-out and self-hosting for reverse geocoding**~~
  - [X] ~~Add `--no-geocode` (no coordinates sent to any third party).~~
  - [X] ~~Add `--nominatim-url` for a custom/self-hosted Nominatim server.~~
  - [X] ~~Enforce Nominatim's ≤1 req/s usage policy (shared rate limiter).~~
  - [ ] Offline reverse geocoding (bundled/local dataset) for full opsec, no network.

### CLI usability

- [X] ~~**Positional target auto-detection**~~
  - [X] ~~`MetaDetective.py <dir|file>` for analysis, `MetaDetective.py <url>` for scraping (with safeguards).~~
  - [X] ~~Default `--download-dir` to ./loot/ and `--depth` to 1.~~

### Metadata extraction robustness

- [ ] **Use exiftool structured JSON output**
  - [ ] Replace per-file `exiftool <file>` + line parsing with `exiftool -j -G` (structured, locale-proof, handles values containing ':').
  - [ ] Batch multiple files / a directory in a single exiftool call (or `-stay_open`) for a large speed-up on big dumps.

### Scraper hardening (OSINT-grade)

- [ ] **Proxy / anonymity**
  - [ ] Add `--proxy` support including SOCKS5/Tor (route requests, avoid burning the source IP).
- [ ] **Resilience**
  - [ ] Retry with exponential backoff + jitter; honor HTTP `Retry-After`.
- [ ] **Politeness**
  - [ ] Optional `--respect-robots` (robots.txt), off by default for authorized testing.
  - [ ] Per-domain concurrency cap.

### Testing

- [ ] **Expand unit test coverage**
  - [ ] Add tests for MetadataExtractor, GPSProcessor, AddressResolver.
  - [ ] Add tests for MetadataExporter (HTML, TXT, JSON outputs).
  - [ ] Add tests for --parse-only and --filter-field flags.

### Website Enhancement

- [ ] **Incorporate Metadata Example Files**
  - [ ] Host a set of diverse example files embedded with metadata on the MetaDetective site.
    - [ ] Ensure these example files cover a wide range of metadata scenarios to showcase MetaDetective's capabilities.
  - [ ] Replace references to "https://example.com" in documentation and demos with links to these metadata example files on the MetaDetective site.
