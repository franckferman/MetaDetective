<div id="top" align="center">

[![Contributors][contributors-shield]](https://github.com/franckferman/MetaDetective/graphs/contributors)
[![Forks][forks-shield]](https://github.com/franckferman/MetaDetective/network/members)
[![Stargazers][stars-shield]](https://github.com/franckferman/MetaDetective/stargazers)
[![Issues][issues-shield]](https://github.com/franckferman/MetaDetective/issues)
[![MIT License][license-shield]](https://github.com/franckferman/MetaDetective/blob/stable/LICENSE)
[![GitHub unittest Workflow Status][unittest-shield]](https://github.com/franckferman/MetaDetective/actions/workflows/unittest.yml)

<div align="center">
<a href="https://github.com/franckferman/MetaDetective">
<img src="https://raw.githubusercontent.com/franckferman/MetaDetective/stable/docs/github/graphical_resources/Logo-Without_background-MetaDetective.png" alt="MetaDetective logo, without background" width="auto" height="auto">
</a>

<h3 align="center">MetaDetective</h3>

<p align="center">
<strong>Delving Deep into File Metadata.</strong>
<br>
Crafted to bridge the gap in metadata extraction and analysis.
<br><br>
<a href="https://github.com/franckferman/MetaDetective/blob/stable/README.md" class="button-style"><strong>Explore the full documentation »</strong></a>
<br><br>
<a href="https://asciinema.org/a/GdFRcXxlnQMcpD6876zVhmpqO" class="button-style">View Demo</a>
.
<a href="https://github.com/franckferman/MetaDetective/issues">Report Bug</a>
·
<a href="https://github.com/franckferman/MetaDetective/issues">Request Feature</a>
</p>

<img src="https://raw.githubusercontent.com/franckferman/MetaDetective/stable/docs/github/graphical_resources/Screenshot-MetaDetective_Demo.png" alt="MetaDetective Demo Screenshot" width="auto" height="auto">

</div>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about">About</a></li>
    <li><a href="#-installation">Installation</a></li>
    <li><a href="#-usage">Usage</a></li>
    <li><a href="#-troubleshooting">Troubleshooting</a></li>
    <li><a href="#-contributing">Contributing</a></li>
    <li><a href="#-license">License</a></li>
    <li><a href="#-contact">Contact</a></li>
  </ol>
</details>

## About

Metadata often holds critical insights in cybersecurity, playing a pivotal role in OSINT and pentesting. With Metagoofil on Kali Linux pivoting away from direct metadata analysis, a gap emerged. Enter MetaDetective: a Python 3 tool adeptly filling this void. It efficiently extracts, categorizes, and displays metadata from single or multiple files, even supporting specific file extensions and result filtering. From author credentials and modification logs to embedded links and software details, and even GPS data, it illuminates potential cybersecurity investigation pathways. While not claiming to be groundbreaking, MetaDetective is undeniably a valuable asset for cybersecurity aficionados.

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🚀 Installation

### Prerequisites

1. **Python 3**: Ensure Python 3 is installed on your system before initiating the installation process.

2. **Exiftool**: Given its simplicity, MetaDetective doesn't rely on any external dependencies or libraries. However, it does necessitate exiftool. Ensure you have exiftool set up on your system.

🔺 **Important**: MetaDetective has been exclusively tested with Python 3.11.4 on Linux and in conjunction with exiftool version 12.56. While the tool might operate on other Python versions, distributions, or exiftool versions, compatibility are only assured with these specific configurations.

### Installation Steps

**Clone the Repository**:

You have a couple of options to clone the repository:

- Using HTTPS:
```bash
git clone https://github.com/franckferman/MetaDetective.git
```

- If you only need the script, you can also directly download it using curl:
```bash
curl -O https://raw.githubusercontent.com/franckferman/MetaDetective/stable/src/MetaDetective/MetaDetective.py
```

This will provide you with the necessary project files.

**Alternative Installation using Pip**:

If you prefer to use the package directly without cloning the repository or to ensure you have the latest stable version, you can install MetaDetective using pip:

1. Create a Virtual Environment:
```bash
python3 -m venv MetaDetectiveEnv
```

2. Activate the Virtual Environment:
```bash
source MetaDetectiveEnv/bin/activate
```

3. Install MetaDetective via Pip:
```bash
pip install MetaDetective
```

By following either of the above methods, you'll have MetaDetective set up and ready to use on your system.

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🎮 Usage

**Examples of Command Usage**:

- Analyzing all files within a directory (with default settings):
```bash
python3 MetaDetective.py -d directory
```

- Analyzing specific files while ignoring certain results and data types:
```bash
python3 MetaDetective.py -d directory -i ^admin anonymous -t doc pdf
```

- Analyzing all types of files within a directory in singular mode display, with a formatted mode type:
```bash
python3 MetaDetective.py -d directory -t all -display singular -format formatted
```

- Analyzing all files within a directory (with default settings) and exporting the results to HTML:
```bash
python3 MetaDetective.py -d directory --export MD_Export-Case_1.html
```

1. **Getting Started**

To begin, you can invoke the help command:
```bash
python3 MetaDetective.py -h
```

2. **Specifying Files for Analysis**

MetaDetective requires at least one file for processing:
```bash
python3 MetaDetective.py -f file
```

For multiple files, use:
```bash
python3 MetaDetective.py -f file1 file2 file3
```

You can also utilize patterns:
```bash
python3 MetaDetective.py -f *specificnameforFiles*
```

Alternatively, specify a directory to process all files within it:
```bash
python3 MetaDetective.py -d directory
```

3. **Additional Parameters**

**Ignoring Specific Results**

Use -i to exclude non-pertinent results:
```bash
python3 MetaDetective.py -d directory -i anonymous
```

Specify multiple ignore terms:
```bash
python3 MetaDetective.py -d directory -i anonymous admin administrateur
```

Regex is also supported:
```bash
python3 MetaDetective.py -d directory -i anonymous ^admin
```

**Specifying Data Type**

The -t option lets you specify data types:
```bash
python3 MetaDetective.py -d directory -t pdf
```

Add multiple data types:
```bash
python3 MetaDetective.py -d directory -t pdf doc
```

To include all types:
```bash
python3 MetaDetective.py -d directory -t all
```

**Display Options**

Use -display to modify the display:
```bash
python3 MetaDetective.py -display all
```

This will show each file with relevant metadata.

For a unique, centralized display without showing each file:
```bash
python3 MetaDetective.py -display singular
```

This option filters and removes duplicates, focusing on singular results.

**Format Options**

When using -display singular, further modify the display:

Use -format formatted for a stylish display (with dashes):
```bash
python3 MetaDetective.py -display all -format formatted
```

Or use -format concise, for a simpler look:
```bash
python3 MetaDetective.py -display all -format concise
```

**Export Options**

The -e or --export option provides the ability to export your metadata results. This can be useful for further analysis, sharing, or for maintaining a record of your findings.

The default export format is HTML. However, for those who have a preference or specific need, we also offer the option to export in TXT format.

- HTML Export (Default):

Execute the following command for a default export:
```bash
python3 MetaDetective.py -d directory -e
```

This command will generate an HTML file with the naming pattern: MetaDetective_Export-<TIMESTAMP>.html.

- TXT Format Export:

If you want your results in TXT format, append the desired format after the --export or -e flag:
```bash
python3 MetaDetective.py -d directory --export txt
```

Keep in mind that the export format can affect the presentation and usability of the data. Make sure to select the format that aligns with your intended use or preference.

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🐳 Docker Integration

MetaDetective offers a Dockerized version for easy setup and consistent execution.

To set up and use MetaDetective with Docker, refer to the Docker-specific documentation available here: [MetaDetective Docker Setup](https://github.com/franckferman/MetaDetective/blob/stable/docker/README.md).

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🔧 Troubleshooting

Encountering issues? Don't worry. If you come across any problems or have questions, please don't hesitate to submit a ticket for assistance: [Submit an issue on GitHub](https://github.com/franckferman/MetaDetective/issues)

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🤝 Contributing

We truly appreciate and welcome community involvement. Your contributions, feedback, and suggestions play a crucial role in improving the project for everyone. If you're interested in contributing or have ideas for enhancements, please feel free to open an issue or submit a pull request on our GitHub repository. Every contribution, no matter how big or small, is highly valued and greatly appreciated!

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 📚 License

This project is licensed under the GNU Affero General Public License, Version 3.0. For more details, please refer to the LICENSE file in the repository: [Read the license on GitHub](https://github.com/franckferman/MetaDetective/blob/stable/LICENSE)

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## Contact

[![ProtonMail][protonmail-shield]](mailto:contact@franckferman.fr) 
[![LinkedIn][linkedin-shield]](https://www.linkedin.com/in/franckferman)

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/franckferman/MetaDetective.svg?style=for-the-badge
[contributors-url]: https://github.com/franckferman/MetaDetective/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/franckferman/MetaDetective.svg?style=for-the-badge
[forks-url]: https://github.com/franckferman/MetaDetective/network/members
[stars-shield]: https://img.shields.io/github/stars/franckferman/MetaDetective.svg?style=for-the-badge
[stars-url]: https://github.com/franckferman/MetaDetective/stargazers
[issues-shield]: https://img.shields.io/github/issues/franckferman/MetaDetective.svg?style=for-the-badge
[issues-url]: https://github.com/franckferman/MetaDetective/issues
[license-shield]: https://img.shields.io/github/license/franckferman/MetaDetective.svg?style=for-the-badge
[license-url]: https://github.com/franckferman/MetaDetective/blob/stable/LICENSE
[unittest-shield]: https://img.shields.io/github/actions/workflow/status/franckferman/MetaDetective/unittest.yml?style=for-the-badge
[protonmail-shield]: https://img.shields.io/badge/ProtonMail-8B89CC?style=for-the-badge&logo=protonmail&logoColor=white
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=blue
