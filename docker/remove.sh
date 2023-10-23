#!/bin/bash

CONTAINER_ID=$(sudo docker ps -aqf "name=metadetective-container" -q)

if [ ! -z "$CONTAINER_ID" ]; then
    echo "Stopping and removing the metadetective-container container..."
    sudo docker rm -f $CONTAINER_ID
else
    echo "No container found: metadetective-container"
fi

IMAGE_EXISTS=$(sudo docker images -q metadetective-image)

if [ ! -z "$IMAGE_EXISTS" ]; then
    read -p "Do you also want to delete the Docker image (metadetective-image)? [y/N] " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        sudo docker rmi $IMAGE_EXISTS
        echo "Docker image metadetective-image deleted."
    fi
else
    echo "No Docker image found: metadetective-image"
fi
