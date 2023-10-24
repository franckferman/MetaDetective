FROM debian:bullseye-slim

LABEL maintainer="Franck FERMAN <contact@franckferman.fr>" \
      description="Unleash Metadata Intelligence with MetaDetective. Your Assistant Beyond Metagoofil." \
      metadetective_version="1.0.6" \
      docker_image_version="1.0.1"

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    libimage-exiftool-perl \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install MetaDetective

ENV PATH="/root/.local/bin:${PATH}"

CMD ["tail", "-f", "/dev/null"]

