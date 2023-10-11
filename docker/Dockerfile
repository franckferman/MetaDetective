FROM debian:bullseye-slim

LABEL maintainer="Franck FERMAN <contact@franckferman.fr>" \
      description="MetaDetective: A Python 3 tool designed for advanced metadata analysis pivotal in OSINT and pentesting." \
      metadetective_version="1.0.2" \
      docker_image_version="1.0.0"

RUN apt-get update && apt-get install -y \
    python3 \
    git \
    libimage-exiftool-perl \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    git -c http.sslVerify=false clone https://github.com/franckferman/MetaDetective.git app

CMD ["tail", "-f", "/dev/null"]

