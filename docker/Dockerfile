FROM debian:bookworm-slim

LABEL maintainer="Franck FERMAN <contact@franckferman.fr>" \
      description="Metadata extraction and web scraping for OSINT and pentesting." \
      metadetective_version="2.0.0"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      python3 \
      python3-pip \
      libimage-exiftool-perl && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --break-system-packages "MetaDetective==2.0.0" && \
    printf '%s\n' \
      '#!/bin/sh' \
      'exec python3 -m MetaDetective.MetaDetective "$@"' \
      > /usr/local/bin/metadetective && \
    chmod +x /usr/local/bin/metadetective

RUN useradd -r -s /bin/false metadetective
USER metadetective

WORKDIR /data

ENTRYPOINT ["metadetective"]
CMD ["--help"]
