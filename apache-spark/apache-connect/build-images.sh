#!/bin/bash

# Script to build Docker images for Spark Connect environment

echo "Building Docker images for Spark Connect environment..."

# Navigate to the script directory
cd "$(dirname "$0")"

# Build the Docker image directly with docker build
echo "Building apache-spark-connect image..."
docker build -t apache-spark-connect:latest .

echo ""
echo "Docker images built successfully!"
echo "To start the environment, run: ./start-environment.sh"
