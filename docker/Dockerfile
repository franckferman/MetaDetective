FROM debian:bookworm-slim

ARG VERSION

LABEL maintainer="Franck FERMAN <contact@franckferman.fr>" \
      description="Metadata extraction and web scraping for OSINT and pentesting." \
      version="${VERSION}"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      python3 \
      python3-pip \
      libimage-exiftool-perl && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --break-system-packages "MetaDetective==${VERSION}"

RUN useradd -r -s /bin/false metadetective
USER metadetective

WORKDIR /data

ENTRYPOINT ["metadetective"]
CMD ["--help"]
