#!/bin/bash

# Script to build Docker images for Spark Connect environment

echo "Building Docker images for Spark Connect environment..."

# Navigate to the script directory
cd "$(dirname "$0")"

# Build the Docker images with no cache to ensure fresh builds
docker-compose build --no-cache

echo ""
echo "Docker images built successfully!"
echo "To start the environment, run: ./start-environment.sh"
