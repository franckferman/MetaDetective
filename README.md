<div id="top" align="center">

<!-- Shields Header -->
[![Contributors][contributors-shield]](https://github.com/franckferman/MetaDetective/graphs/contributors)
[![Forks][forks-shield]](https://github.com/franckferman/MetaDetective/network/members)
[![Stargazers][stars-shield]](https://github.com/franckferman/MetaDetective/stargazers)
[![Issues][issues-shield]](https://github.com/franckferman/MetaDetective/issues)
[![MIT License][license-shield]](https://github.com/franckferman/MetaDetective/blob/stable/LICENSE)
[![GitHub unittest Workflow Status][unittest-shield]](https://github.com/franckferman/MetaDetective/actions/workflows/unittest.yml)

<!-- Logo -->
<a href="https://github.com/franckferman/MetaDetective">
  <img src="https://raw.githubusercontent.com/franckferman/MetaDetective/stable/docs/github/graphical_resources/Logo-Without_background-MetaDetective.png" alt="MetaDetective Logo" width="auto" height="auto">
</a>

<!-- Title & Tagline -->
<h3 align="center">🕵️‍♂️ MetaDetective</h3>
<p align="center">
    <em>Unleash Metadata Intelligence with MetaDetective.</em>
    <br>
    Bridging the chasm in metadata extraction and analysis.
</p>

<!-- Links & Demo -->
<p align="center">
    <a href="https://github.com/franckferman/MetaDetective/blob/stable/README.md" class="button-style"><strong>📘 Explore the full documentation</strong></a>
    ·
    <a href="https://asciinema.org/a/55mEbe7GFVfIJ6OSfjOaDeYLv" class="button-style">🎥 View Demo</a>
    ·
    <a href="https://github.com/franckferman/MetaDetective/issues">🐞 Report Bug</a>
    ·
    <a href="https://github.com/franckferman/MetaDetective/issues">🛠️ Request Feature</a>
</p>

https://github.com/franckferman/MetaDetective/assets/73023545/7b245f87-37e2-40b7-8b3c-88aefecb4e13  

</div>

## 📜 Table of Contents

<details open>
  <summary><strong>Click to collapse/expand</strong></summary>
  <ol>
    <li><a href="#-about">📖 About</a></li>
    <li><a href="#-installation">🛠️ Installation</a></li>
    <li><a href="#-usage">🎮 Usage</a></li>
    <li><a href="#-troubleshooting">❗ Troubleshooting</a></li>
    <li><a href="#-contributing">🤝 Contributing</a></li>
    <li><a href="#-star-evolution">🌠 Star Evolution</a></li>
    <li><a href="#-license">📜 License</a></li>
    <li><a href="#-contact">📞 Contact</a></li>
  </ol>
</details>

## 📖 About

**MetaDetective:** _Advanced metadata analysis and web scraping._

Metadata, in the realm of cybersecurity, is more than just embedded information; it's a gateway to insightful perspectives, often unveiling crucial leads in OSINT and pentesting.

As key tools like Metagoofil on Kali Linux shifted their trajectory away from pure metadata analysis, the exigency for a robust alternative took center stage. Enter **MetaDetective**.

### 🧠 Tailored Metadata Analysis

Drawing inspiration from the foundational tools like Metagoofil, MetaDetective emerges as a revitalized and improved iteration, dedicated to providing efficient metadata extraction and presentation. It stands out as a comprehensive Python 3 tool, purposely designed to bridge the existing gaps in metadata analysis.

### 📊 Streamlined Data Presentation

Beyond mere extraction, MetaDetective prides itself on its capability to meticulously categorize and showcase metadata. Whether dealing with an individual file or an array of them, the tool ensures users grasp the entire spectrum of data, both in its breadth and depth.

<p align="center">
  <img src="https://raw.githubusercontent.com/franckferman/MetaDetective/stable/docs/github/graphical_resources/Screenshot-MetaDetective_Demo.png" alt="MetaDetective Demo Screenshot" width="auto" height="auto">
</p>

### 🌐 Web Scraping

While Metagoofil once leaned on Google searches—a method riddled with IP restrictions and the labyrinth of proxy workarounds—MetaDetective pioneers a path with direct web scraping. By targeting sites directly, it sidesteps disruptions, delivering a dataset that's not just richer, but also more precise, spotlighting potential data leaks.

<p align="center">
  <img src="https://raw.githubusercontent.com/franckferman/MetaDetective/stable/docs/github/graphical_resources/Screenshot-MetaDetective_Scraping_Demo.png" alt="MetaDetective Scraping Demo Screenshot" width="auto" height="auto">
</p>

### 🔍 Complementary Utility for OSINT and Pentesting

Although it is now independent and offers its own functions, including scraping, MetaDetective isn't just a standalone behemoth. It's crafted for seamless integration and synergy with tools like Metagoofil. A quintessential addition to every pentester's and OSINT researcher's toolkit, MetaDetective magnifies data acquisition prowess and broadens the horizons of analysis.

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🚀 Installation

Before diving into the installation process, ensure you meet the following prerequisites.

### Prerequisites

1. **Python 3**: Ensure Python 3 is installed on your system before initiating the installation process.

2. **Exiftool**: Given its simplicity, MetaDetective doesn't rely on any external dependencies or libraries. However, it does necessitate exiftool. Ensure you have exiftool set up on your system.

> ⚠️ **Note**: MetaDetective has been rigorously tested with Python 3.11.4 on Linux alongside exiftool version 12.56. While it may function with other versions, compatibility is guaranteed only with these specific configurations.

### Installation methods

1. **Git clone the repository**:
```bash
git clone https://github.com/franckferman/MetaDetective.git
```

2. **Direct download**:
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

4. **Docker integration**:

For a Docker-based setup, refer to our Docker-specific guide: [MetaDetective Docker Setup](https://github.com/franckferman/MetaDetective/blob/stable/docker/README.md).

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🎮 Usage

Ensure you adapt your command according to how you've set up `MetaDetective`.

### **Getting started**

Kick off with the built-in help to explore MetaDetective's functionalities:

```bash
python3 src/MetaDetective/MetaDetective.py -h
```

### **Command examples**

#### 🕵️ File analysis:

| Task | Command |
| --- | --- |
| Analyze all files in directory | `python3 src/MetaDetective/MetaDetective.py -d examples/` |
| Specific types & ignore patterns | `python3 src/MetaDetective/MetaDetective.py -d examples/ -i ^admin anonymous -t doc pdf` |
| Display all results for each file | `python3 src/MetaDetective/MetaDetective.py -d examples/ -t all --display all` |

#### 🔎 Export function:

| Task | Command |
| --- | --- |
| Default export (HTML) | `python3 src/MetaDetective/MetaDetective.py -d examples/ --export` |
| Formatted display, txt export | `python3 src/MetaDetective/MetaDetective.py -d examples ---format formatted -e txt -o ~/` |

#### 🌐 Web Scraping:

| Task | Command |
| --- | --- |
| Scan without downloading | `python3 src/MetaDetective/MetaDetective.py --scraping --scan --url https://example.com/` |
| Scan without downloading PDF files only | `python3 src/MetaDetective/MetaDetective.py --scraping --scan --url https://example.com/ --extensions pdf` |
| Download to specified directory | `python3 src/MetaDetective/MetaDetective.py --scraping --download-dir ~ --url https://example.com/` |
| Download with set depth | `python3 src/MetaDetective/MetaDetective.py --scraping --depth 1 --download-dir ~ --url https://example.com/` |

### **Additional parameters**

#### 🌐 Web Scraping:

To initiate the web scraping mode, use the `--scraping` flag. Remember, this option doesn't function independently. It requires either a scanning or downloading parameter.

- **Activating web scraping mode**: 
```bash
python3 src/MetaDetective/MetaDetective.py --scraping
```

- **Scanning and displaying statistics**: 
Ensure both the URL and `--scan` flags are used.
```bash
python3 src/MetaDetective/MetaDetective.py --scraping --scan --url https://example.com
```

- **Downloading web content**:
Indicate the desired directory using `--download-dir` and provide the target URL.
```bash
python3 src/MetaDetective/MetaDetective.py --scraping --download-dir ~ --url https://example.com
```

- **Adjusting scraping depth**:
Use the `--depth` flag to specify how deeply the scraper should navigate through links.
```bash
python3 src/MetaDetective/MetaDetective.py --scraping --scan --url https://aulnay-sous-bois.fr --depth 1
```

##### **Additional Flags**:

- **External link tracking**: 
Use `--follow-extern` to allow tracking of external links (those outside the base URL). Typically not advised, but might be useful in certain contexts.

- **Thread management**: 
Use `--threads` to specify the number of threads for concurrent operations.

- **Rate limiting**:
Use `--rate` to control the maximum number of requests per second.

#### 🕵️ File analysis & Metadata Analyzer:

##### **Basic Commands**:

To begin analyzing files, you'll use either the `-d` or `-f` flag.

- `-d` or `--directory`: Select a directory containing one or multiple files.
- `-f` or `--files`: Choose a single or multiple specific files.

Analyze the contents of a directory.
```bash
python3 src/MetaDetective/MetaDetective.py -d examples
```

Analyze the contents of a file.
```bash
python3 src/MetaDetective/MetaDetective.py -f examples/MetaDetective.docx
```

Analyze the contents of multiple files.
```bash
python3 src/MetaDetective/MetaDetective.py -f examples/MetaDetective-APTX_4869_report.pdf examples/MetaDetective-Kogoro_s_Choice.pdf
```

##### **Specifying data type**

You can filter to analyze specific file types:

| Task | Command |
| --- | --- |
| Specify a data type | `python3 src/MetaDetective/MetaDetective.py -d directory -t pdf` |
| Add multiple data types | `python3 src/MetaDetective/MetaDetective.py -d directory -t pdf doc` |
| Include all types | `python3 src/MetaDetective/MetaDetective.py -d directory -t all` |

##### **Ignoring specific results**:

If you want to omit specific keywords from the displayed metadata, use the `-i` or `--ignore` flag. For instance, you might want to exclude common usernames like "admin" during the reconnaissance phase of your pentest. Regex patterns are supported, e.g., `^BeginBy`.

| Task | Command |
| --- | --- |
| Exclude specific results | `python3 src/MetaDetective/MetaDetective.py -d directory -i anonymous` |
| Exclude multiple terms | `python3 src/MetaDetective/MetaDetective.py -d directory -i anonymous admin administrateur` |
| Regex exclusions | `python3 src/MetaDetective/MetaDetective.py -d directory -i anonymous ^admin` |

##### **Display options**

Adapt the display of your results to suit your preferences:

| Task | Command |
| --- | --- |
| Show each file's metadata | `python3 src/MetaDetective/MetaDetective.py --display all` |
| Singular results without duplicates | `python3 src/MetaDetective/MetaDetective.py --display singular` |

##### **Format options**

Modify your display further with these:

| Task | Command |
| --- | --- |
| Stylish display | `python3 src/MetaDetective/MetaDetective.py --display all --format formatted` |
| Simpler look | `python3 src/MetaDetective/MetaDetective.py --display all --format concise` |

#### 🔎 **Export options**

MetaDetective provides flexibility in exporting analysis results.

By default, using the `--export` or `-e` option will save your results in an HTML format. This design ensures a visually appealing report for your analysis.

If you prefer a `.txt` format, that's possible too. Switch between formats using the `-e` or `--export` flag followed by the desired format: `-e txt` or `-e pdf`.

The export will, by default, use a predefined name appended with a timestamp. To customize this name, you can append a suffix using the `-c` or `--custom` flag.

Further, the `--out` or `-o` argument lets you specify the directory path for your exported data.

**Be aware**: The `display` and `format` options, as previously discussed, will influence the presentation of your exported document, whether in HTML or TXT format. Data representation might differ between the two formats.

| Task | Description | Command |
| --- | --- | --- |
| HTML Export (Default) | Produces an HTML file named: `MetaDetective_Export-<TIMESTAMP>.html`. | `python3 src/MetaDetective/MetaDetective.py -d directory -e` |
| TXT Format Export | Save results in TXT format. | `python3 src/MetaDetective/MetaDetective.py -d directory --export txt` |
| Custom Filename Suffix | Add a custom suffix to the filename. | `python3 src/MetaDetective/MetaDetective.py -d directory -e --custom Pentest-MD_2` |
| Specify Output Directory | Define the directory for data export. | `python3 src/MetaDetective/MetaDetective.py -d directory -e -o directory` |

<p align="center">
  <img src="https://raw.githubusercontent.com/franckferman/MetaDetective/stable/docs/github/graphical_resources/Screenshot-MetaDetective_HTML_Export_Demo.png" alt="MetaDetective HTML Export Demo Screenshot" width="auto" height="auto">
</p>

**Note**: The export format can greatly affect data presentation and accessibility. Opt for the format that aligns with your requirements.

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🔧 Troubleshooting

Encountering issues? Don't worry. If you come across any problems or have questions, please don't hesitate to submit a ticket for assistance: [Submit an issue on GitHub](https://github.com/franckferman/MetaDetective/issues)

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🤝 Contributing

We truly appreciate and welcome community involvement. Your contributions, feedback, and suggestions play a crucial role in improving the project for everyone. If you're interested in contributing or have ideas for enhancements, please feel free to open an issue or submit a pull request on our GitHub repository. Every contribution, no matter how big or small, is highly valued and greatly appreciated!

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 🌠 Star Evolution

Explore the star history of this project and see how it has evolved over time:

<a href="https://star-history.com/#franckferman/MetaDetective&Timeline">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=franckferman/MetaDetective&type=Timeline&theme=dark" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=franckferman/MetaDetective&type=Timeline" />
  </picture>
</a>

Your support is greatly appreciated. We're grateful for every star! Your backing fuels our passion. ✨

## 📚 License

This project is licensed under the GNU Affero General Public License, Version 3.0. For more details, please refer to the LICENSE file in the repository: [Read the license on GitHub](https://github.com/franckferman/MetaDetective/blob/stable/LICENSE)

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## 📞 Contact

[![ProtonMail][protonmail-shield]](mailto:contact@franckferman.fr) 
[![LinkedIn][linkedin-shield]](https://www.linkedin.com/in/franckferman)
[![Twitter][twitter-shield]](https://www.twitter.com/franckferman)

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
[protonmail-shield]: https://img.shields.io/badge/ProtonMail-8B89CC?style=for-the-badge&logo=protonmail&logoColor=blueviolet
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=blue
[twitter-shield]: https://img.shields.io/badge/-Twitter-black.svg?style=for-the-badge&logo=twitter&colorB=blue
