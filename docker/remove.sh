#!/bin/bash

IMAGE_NAME="metadetective-image"
CONTAINER_NAME="metadetective-container"

# Check if container is running
CONTAINER_ID=$(sudo docker ps -aqf "name=$CONTAINER_NAME" -q)

if [ ! -z "$CONTAINER_ID" ]; then
    echo "Stopping and removing the $CONTAINER_NAME container..."
    if ! sudo docker rm -f $CONTAINER_ID; then
        echo "Error removing container $CONTAINER_NAME." >&2
        exit 1
    fi
else
    echo "No container found: $CONTAINER_NAME"
fi

# Check if image exists
IMAGE_EXISTS=$(sudo docker images -q $IMAGE_NAME)

if [ ! -z "$IMAGE_EXISTS" ]; then
    read -p "Do you also want to delete the Docker image ($IMAGE_NAME)? [y/N] " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        if ! sudo docker rmi $IMAGE_EXISTS; then
            echo "Error deleting Docker image $IMAGE_NAME." >&2
            exit 1
        fi
        echo "Docker image $IMAGE_NAME deleted."
    fi
else
    echo "No Docker image found: $IMAGE_NAME"
fi
