FROM debian:bullseye-slim

LABEL maintainer="Franck FERMAN <contact@franckferman.fr>" \
      description="Unleash Metadata Intelligence with MetaDetective." \
      metadetective_version="1.0.9" \
      docker_image_version="1.0.2"

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    libimage-exiftool-perl \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install MetaDetective && \
    rm -rf ~/.cache/pip

ENV PATH="/root/.local/bin:${PATH}"

CMD ["tail", "-f", "/dev/null"]
