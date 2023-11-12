## TODO

### Metadata enhancements

- [X] ~~**GPS and photo metadata improvements**~~
  - [X] ~~Add missing metadata fields, especially for geolocation, camera model name, and other device-specific information for images.~~
  - [X] ~~Develop a function to convert GPS data to OSM or Google Maps links.~~

### Data export features

- [X] ~~**Support various export formats**~~
  - [X] ~~Added support for exporting data in HTML format.~~
  - [X] ~~Added support for exporting data in TXT format.~~
  - [X] ~~Implement customizable export options for users.~~
  - [X] ~~Implement advanced customizable export options for users.~~

### GitHub Actions

- [X] ~~**PyPI Automatic Upload on Release**~~
  - [X] ~~Integrate GitHub Actions to trigger PyPI package upload on every new release.~~

### Advanced Filtering

- [ ] **Enhanced Filtering Capabilities**
  - [X] ~~Add support for scraping filter options.~~
  - [ ] Implement local filtering based on sections like "Author" and "Last Modified By".

### Performance Enhancements

- [ ] **Optimize File Comparison for Duplication Avoidance**
  - [ ] Replace SHA256 hash verification with a less resource-intensive method.
    - [ ] Research and evaluate the use of CRC32, or equivalent alternatives, for quick file comparison.
    - [ ] Implement CRC32 or chosen alternative for file integrity checks aimed at duplication avoidance rather than secure cryptographic verification.

### Website Enhancement

- [ ] **Incorporate Metadata Example Files**
  - [ ] Host a set of diverse example files embedded with metadata on the MetaDetective site.
    - [ ] Ensure these example files cover a wide range of metadata scenarios to showcase MetaDetective’s capabilities.
  - [ ] Replace references to "https://example.com" in documentation and demos with links to these metadata example files on the MetaDetective site.
    - [ ] Update documentation and tutorials to direct users to these specific examples for more relevant and practical demonstrations of MetaDetective's functionalities.
