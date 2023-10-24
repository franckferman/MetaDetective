<div id="top" align="center">

[![Contributors][contributors-shield]](https://github.com/franckferman/MetaDetective/graphs/contributors)
[![Forks][forks-shield]](https://github.com/franckferman/MetaDetective/network/members)
[![Stargazers][stars-shield]](https://github.com/franckferman/MetaDetective/stargazers)
[![Issues][issues-shield]](https://github.com/franckferman/MetaDetective/issues)
[![MIT License][license-shield]](https://github.com/franckferman/MetaDetective/blob/stable/LICENSE)
[![GitHub unittest Workflow Status][unittest-shield]](https://github.com/franckferman/MetaDetective/actions/workflows/unittest.yml)

<a href="https://github.com/franckferman/MetaDetective">
<img src="https://raw.githubusercontent.com/franckferman/MetaDetective/stable/docs/github/graphical_resources/Logo-Without_background-MetaDetective.png" alt="MetaDetective logo, without background" width="auto" height="auto">
</a>

<h3 align="center">MetaDetective</h3>

<p align="center">
<strong>Unleash Metadata Intelligence with MetaDetective.</strong>
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

## Table of Contents

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

<b>MetaDetective: Advanced metadata extraction and direct web scraping.</b>

Metadata, in the realm of cybersecurity, is more than just embedded information; it's a gateway to insightful perspectives, often unveiling crucial leads in OSINT and pentesting. MetaDetective was born out of the need to offer a potent solution, especially as prominent tools like Metagoofil on Kali Linux shifted their focus away from direct metadata analysis.

<b>Tailored Metadata Analysis</b>:

Drawing inspiration from the foundational tools like Metagoofil, MetaDetective emerges as a revitalized and improved iteration, dedicated to providing efficient metadata extraction and presentation. It stands out as a comprehensive Python 3 tool, purposely designed to bridge the existing gaps in metadata analysis.

<b>Streamlined Data Presentation</b>:

With its capability to seamlessly extract, categorize, and exhibit metadata from single to multiple files, it ensures users have both the breadth and depth of data at their disposal.

<b>Direct web scraping</b>:

Where Metagoofil relies on Google searches — a method fraught with IP restrictions and the need for complex proxy workarounds — MetaDetective advances with its direct web scraping capability. By targeting websites directly, it minimizes disruptions and offers a richer and more accurate dataset, highlighting potential information leaks.

<b>Complementary Utility for OSINT and Pentesting</b>:

While functioning as a standalone powerhouse, MetaDetective is also optimized for symbiotic utility alongside tools like Metagoofil. It's a must-have in the toolkit of every pentester and OSINT researcher, accentuating data gathering capabilities and enriching the analysis spectrum.

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🚀 Installation

Before diving into the installation process, ensure you meet the following prerequisites.

### Prerequisites

1. **Python 3**: Ensure Python 3 is installed on your system before initiating the installation process.

2. **Exiftool**: Given its simplicity, MetaDetective doesn't rely on any external dependencies or libraries. However, it does necessitate exiftool. Ensure you have exiftool set up on your system.

> ⚠️ **Note**: MetaDetective has been rigorously tested with Python 3.11.4 on Linux alongside exiftool version 12.56. While it may function with other versions, compatibility is guaranteed only with these specific configurations.

### Installation Methods

1. **Git Clone the Repository**:
```bash
git clone https://github.com/franckferman/MetaDetective.git
```

2. **Direct Download**:
To skip cloning and directly download the script (designed for simplicity and flexibility, it doesn't depend on any external packages, so if you only need the script, you can also directly download it):
```bash
curl -O https://raw.githubusercontent.com/franckferman/MetaDetective/stable/src/MetaDetective/MetaDetective.py
```

3. **Pip Installation**:

- Create & Activate a Virtual Environment:
```bash
python3 -m venv MetaDetectiveEnv
source MetaDetectiveEnv/bin/activate
```

- Install MetaDetective:
```bash
pip install MetaDetective
```

4. **Docker Integration**:

For a Docker-based setup, refer to our Docker-specific guide: [MetaDetective Docker Setup](https://github.com/franckferman/MetaDetective/blob/stable/docker/README.md).

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🎮 Usage

Ensure you adapt your command according to how you've set up `MetaDetective`.

### **Getting Started**

Kick off with the built-in help to explore MetaDetective's functionalities:

```bash
python3 src/MetaDetective/MetaDetective.py -h
```

### **Command Examples**

#### File Analysis:

| Task | Command |
| --- | --- |
| Analyze all files in directory | `python3 src/MetaDetective/MetaDetective.py -d examples/` |
| Specific types & ignore patterns | `python3 src/MetaDetective/MetaDetective.py -d examples/ -i ^admin anonymous -t doc pdf` |
| Display all results for each file | `python3 src/MetaDetective/MetaDetective.py -d examples/ -t all --display all` |

#### File Analysis & Export:

| Task | Command |
| --- | --- |
| Default export (HTML) | `python3 src/MetaDetective/MetaDetective.py -d examples/ --export` |
| Formatted display, txt export | `python3 src/MetaDetective/MetaDetective.py -d examples ---format formatted -e txt -o ~/` |

#### Web Scraping:

| Task | Command |
| --- | --- |
| Scan without downloading | `python3 src/MetaDetective/MetaDetective.py --scraping --scan --url https://example.com/` |
| Download to specified directory | `python3 src/MetaDetective/MetaDetective.py --scraping --download-dir ~ --url https://example.com/` |
| Download with set depth | `python3 src/MetaDetective/MetaDetective.py --scraping --depth 1 --download-dir ~ --url https://example.com/` |

### **Additional Parameters**

Dive deeper into MetaDetective's functionalities using additional parameters.

#### **Ignoring Specific Results**

To focus on pertinent results, filter out the noise:

| Task | Command |
| --- | --- |
| Exclude specific results | `python3 src/MetaDetective/MetaDetective.py -d directory -i anonymous` |
| Exclude multiple terms | `python3 src/MetaDetective/MetaDetective.py -d directory -i anonymous admin administrateur` |
| Regex exclusions | `python3 src/MetaDetective/MetaDetective.py -d directory -i anonymous ^admin` |

#### **Specifying Data Type**

Customize the type of data you analyze:

| Task | Command |
| --- | --- |
| Specify a data type | `python3 src/MetaDetective/MetaDetective.py -d directory -t pdf` |
| Add multiple data types | `python3 src/MetaDetective/MetaDetective.py -d directory -t pdf doc` |
| Include all types | `python3 src/MetaDetective/MetaDetective.py -d directory -t all` |

#### **Display Options**

Adapt the display of your results to suit your preferences:

| Task | Command |
| --- | --- |
| Show each file's metadata | `python3 src/MetaDetective/MetaDetective.py --display all` |
| Singular results without duplicates | `python3 src/MetaDetective/MetaDetective.py --display singular` |

#### **Format Options**

Modify your display further with these:

| Task | Command |
| --- | --- |
| Stylish display | `python3 src/MetaDetective/MetaDetective.py --display all --format formatted` |
| Simpler look | `python3 src/MetaDetective/MetaDetective.py --display all --format concise` |

#### **Export Options**

Document your findings with export options:

| Task | Description | Command |
| --- | --- | --- |
| HTML Export (Default) | Generates an HTML file following the pattern: MetaDetective_Export-<TIMESTAMP>.html. | `python3 src/MetaDetective/MetaDetective.py -d directory -e` |
| TXT Format Export | Output your results in TXT format. | `python3 src/MetaDetective/MetaDetective.py -d directory --export txt` |

**Note**: The export format influences the presentation and usability of data. Choose the format that matches your needs.

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
