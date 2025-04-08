#!/bin/bash

# Script to start the Spark Connect environment

echo "Starting Spark Connect environment..."

# Navigate to the script directory
cd "$(dirname "$0")"

# Start the Docker Compose environment in detached mode
docker-compose up -d

echo "Waiting for services to initialize..."
sleep 5

# Check if services are running
docker-compose ps

echo ""
echo "Spark Connect environment is now running!"
echo "Access Spark Master UI at: http://localhost:8080"
echo "Access Spark Connect UI at: http://localhost:4040 (during application execution)"
echo ""
echo "To test the connection, run: python test_connection.py"
echo "To analyze movie similarities, run: python movie-similarities-local.py <movie_id>"
