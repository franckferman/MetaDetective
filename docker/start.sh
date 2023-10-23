#!/bin/bash

IMAGE_EXISTS=$(sudo docker images -q metadetective-image)

if [ -z "$IMAGE_EXISTS" ]; then
    echo "Building Docker image..."
    sudo docker build -t metadetective-image .
else
    echo "Using existing Docker image..."
fi

CONTAINER_ID=$(sudo docker ps -aqf "name=metadetective-container")

if [ ! -z "$CONTAINER_ID" ]; then
    echo "Stopping existing container..."
    sudo docker stop metadetective-container
    echo "Removing existing container..."
    sudo docker rm metadetective-container
fi

echo "Running container..."
sudo docker run -d --rm --name metadetective-container metadetective-image

echo "Entering container shell..."
sudo docker exec -it metadetective-container /bin/bash
