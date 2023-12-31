# MetaDetective Docker Setup <a name="top"></a>

This document offers instructions on how to set up and utilize the Dockerized version of MetaDetective.

## Table of Contents

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#using-pre-built-image">Using the Pre-built Image</a></li>
    <li><a href="#dockerfile-details">Dockerfile Details</a></li>
  </ol>
</details>

## Getting Started <a name="getting-started"></a>

### Prerequisites <a name="prerequisites"></a>

- Docker must be installed on your machine.
- While the Docker image can technically be run on Windows, the provided scripts are written in Bash. Thus, they are designed for environments that support Bash scripting, like Linux.

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

### Building the Docker Image <a name="building-the-docker-image"></a>

To build and run the Docker image:
```bash
# ./start.sh
```

When executed, this script performs the following actions:
1. It checks if the metadetective-image already exists. If it doesn't, the script builds one using the provided Dockerfile.
2. It runs a container named metadetective-container.
3. Upon completion, you'll be placed inside the container shell, where you're ready to start using MetaDetective.
<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

### Stopping and Removing Containers and Images <a name="stopping-and-removing-containers-and-images"></a>

In case you want to stop the running container and/or remove the Docker image:
```bash
# ./remove.sh
```

Executing this script will:
1. Stop and remove the metadetective-container if it's currently running.
2. Prompt you with the option to delete the metadetective-image.

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## Using the Pre-built Image <a name="using-pre-built-image"></a>

If you'd rather use the pre-built Docker image from Docker Hub, follow these steps:

### Pulling the Image <a name="pulling-the-image"></a>

Retrieve the Docker image using:
```bash
# docker pull franckferman/metadetective
```

### Running the Container <a name="running-the-container"></a>

Start a container based on the image:
```bash
# docker run -it --name metadetective franckferman/metadetective /bin/bash
```

### Stopping the Container

```bash
# docker stop metadetective
```

This command will stop the container named "metadetective".

### Removing the Container

Once the container is stopped, you can remove it using:
```bash
# docker rm metadetective
```

This command will remove the container named "metadetective".

### Troubleshooting container deletion problems

1. List All Containers (including stopped ones):
```bash
# docker ps -a
```

Check if the container "metadetective" is listed. If it's listed, note the container ID.

2. Force Remove the Container:
```bash
# docker rm -f metadetective
```

Alternatively, if using the container ID:
```bash
# docker rm -f [CONTAINER_ID]
```

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>

## Dockerfile Details <a name="dockerfile-details"></a>

Our Docker image is built upon the lightweight foundation of `debian:bullseye-slim`. 

The following essential packages are installed:

`python3`: The core programming language for running MetaDetective.

`python3-pip`: Used specifically to fetch and install the MetaDetective release directly from PyPI.

`libimage-exiftool-perl`: MetaDetective partly relies on this tool for metadata extraction and analysis.

Due to the ENV PATH="/root/.local/bin:${PATH}" setting in the Dockerfile, you can directly launch MetaDetective within the container without needing to navigate to any specific directory. Simply invoke MetaDetective followed by the desired command-line arguments.

<p align="right">(<a href="#top">🔼 Back to top</a>)</p>
