<div id="top" align="center">

[![Contributors][contributors-shield]](https://github.com/franckferman/MetaDetective/graphs/contributors)
[![Forks][forks-shield]](https://github.com/franckferman/MetaDetective/network/members)
[![Stargazers][stars-shield]](https://github.com/franckferman/MetaDetective/stargazers)
[![Issues][issues-shield]](https://github.com/franckferman/MetaDetective/issues)
[![MIT License][license-shield]](https://github.com/franckferman/MetaDetective/blob/main/LICENSE)

<div align="center">
<a href="https://github.com/franckferman/MetaDetective">
<img src="./docs/github/graphical_resources/Logo-Without_background-MetaDetective.png" alt="MetaDetective logo, without background" width="auto" height="auto">
</a>

<h3 align="center">MetaDetective</h3>

<p align="center">
<strong>Delving Deep into File Metadata.</strong>
<br>
Crafted to bridge the gap in metadata extraction and analysis.
<br><br>
<a href="https://github.com/franckferman/MetaDetective/blob/master/README.md" class="button-style"><strong>Explore the full documentation »</strong></a>
<br><br>
<a href="https://asciinema.org/a/GdFRcXxlnQMcpD6876zVhmpqO" class="button-style">View Demo</a>
.
<a href="https://github.com/franckferman/MetaDetective/issues">Report Bug</a>
·
<a href="https://github.com/franckferman/MetaDetective/issues">Request Feature</a>
</p>

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

In the intricate landscape of cybersecurity, metadata stands sometimes as a goldmine of information. From the shadows of a pentesting reconnaissance mission to the foreground of Open Source Intelligence (OSINT) undertakings, these subtle snippets of data often carry revelatory insights. MetaDetective, a Python 3 tool, is meticulously engineered to sift through, extract, and elegantly display this trove.

In its recent version on Kali Linux, Metagoofil shifted its focus away from direct metadata analysis, as Kali's official documentation indicates a choice to rely on external utilities like exiftool.

While designed primarily to address the gap left by Metagoofil, MetaDetective's functionality extends beyond this scope, proving beneficial even outside of Metagoofil's context. Responding adeptly to this need, MetaDetective offers a versatile approach. Whether you're focusing on a single file, a collection of files, an entire directory, or even refining your search by specific file extensions, this tool has got you covered. Additional features allow for result filtering using keywords or regex, tailored formatting options, and deduplication to provide a concise, centralized display of results. Through its autonomous extraction, categorization, and presentation, MetaDetective showcases vital metadata points—author credentials, modification records, embedded hyperlinks, and the software tools used, among others. Each metadata element can be instrumental, potentially reshaping the trajectory of a cybersecurity probe.

While MetaDetective may not brand itself as revolutionary, it confidently stands as an essential addition to the toolkit of cybersecurity professionals and enthusiasts alike.

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

- Using GitHub CLI:
```bash
gh repo clone franckferman/MetaDetective
```

- If you only need the script, you can also directly download it using curl:
```bash
curl -O https://raw.githubusercontent.com/franckferman/MetaDetective/master/MetaDetective/MetaDetective.py
```

This will provide you with the necessary project files.

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

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🔧 Troubleshooting

Encountering issues? Don't worry. If you come across any problems or have questions, please don't hesitate to submit a ticket for assistance: [Submit an issue on GitHub](https://github.com/franckferman/MetaDetective/issues)

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🤝 Contributing

We truly appreciate and welcome community involvement. Your contributions, feedback, and suggestions play a crucial role in improving the project for everyone. If you're interested in contributing or have ideas for enhancements, please feel free to open an issue or submit a pull request on our GitHub repository. Every contribution, no matter how big or small, is highly valued and greatly appreciated!

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 📚 License

This project is licensed under the GNU Affero General Public License, Version 3.0. For more details, please refer to the LICENSE file in the repository: [Read the license on GitHub](https://github.com/franckferman/MetaDetective/blob/master/LICENSE)

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## Contact

[![ProtonMail][protonmail-shield]](mailto:fferman@protonmail.ch) 
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
[license-url]: https://github.com/franckferman/MetaDetective/blob/master/LICENSE
[protonmail-shield]: https://img.shields.io/badge/ProtonMail-8B89CC?style=for-the-badge&logo=protonmail&logoColor=white
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=blue
