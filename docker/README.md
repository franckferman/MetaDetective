# MetaDetective Docker Setup

MetaDetective is a Python 3 tool designed for advanced metadata analysis pivotal in OSINT and pentesting. This document provides guidance on using the Dockerized version of MetaDetective.

## Getting Started

### Prerequisites

- Docker installed on your machine.

### Building the Docker Image

To build and run the Docker image:

```bash
sudo ./start.sh
```

This script:

1. Checks if the `metadetective-image` already exists and builds one if not using the provided `Dockerfile`.
2. Runs the container named `metadetective-container`.
3. Places you inside the container shell, where you can start using MetaDetective.

### Stopping and Removing Containers and Images

To stop the running container and optionally remove the image:

```bash
sudo ./remove.sh
```

This script:

1. Stops and removes the `metadetective-container` if it's running.
2. Prompts you if you want to remove the `metadetective-image`.

## Dockerfile Details

The Docker image is based on `debian:bullseye-slim` and installs:

- python3
- git
- libimage-exiftool-perl

MetaDetective is cloned directly from its GitHub repository into the `app` directory within the container.
