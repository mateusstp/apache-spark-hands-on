#!/bin/bash

# Script to stop the Spark Connect environment

echo "Stopping Spark Connect environment..."

# Navigate to the script directory
cd "$(dirname "$0")"

# Stop the Docker Compose environment and remove containers
docker-compose down

echo ""
echo "Spark Connect environment has been stopped."
echo "To start it again, run: ./start-environment.sh"
