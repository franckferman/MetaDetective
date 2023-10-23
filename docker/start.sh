#!/bin/bash

IMAGE_NAME="metadetective-image"
CONTAINER_NAME="metadetective-container"

# Check if image exists
IMAGE_EXISTS=$(sudo docker images -q $IMAGE_NAME)

if [ -z "$IMAGE_EXISTS" ]; then
    echo "Building Docker image..."
    if ! sudo docker build -t $IMAGE_NAME .; then
        echo "Error building Docker image." >&2
        exit 1
    fi
else
    echo "Using existing Docker image..."
fi

# Check if container is running
CONTAINER_ID=$(sudo docker ps -aqf "name=$CONTAINER_NAME")

if [ ! -z "$CONTAINER_ID" ]; then
    echo "Stopping existing container..."
    sudo docker stop $CONTAINER_NAME
    echo "Removing existing container..."
    sudo docker rm $CONTAINER_NAME
fi

# Run the container
echo "Running new container..."
if ! sudo docker run -d --rm --name $CONTAINER_NAME $IMAGE_NAME; then
    echo "Error running container." >&2
    exit 1
fi

# Enter the container shell
echo "Entering container shell..."
sudo docker exec -it $CONTAINER_NAME /bin/bash
