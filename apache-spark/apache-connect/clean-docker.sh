#!/bin/bash

# Script to clean Docker resources (containers, images, networks, volumes)

echo "=== Docker Cleanup Script ==="
echo "This script will clean up Docker resources."

# Check for deep clean flag
DEEP_CLEAN=false
if [ "$1" = "-a" ] || [ "$1" = "--all" ]; then
  DEEP_CLEAN=true
  echo "\n!!! WARNING: Deep clean mode activated !!!"
  echo "This will remove ALL Docker resources, including running containers."
  read -p "Are you sure you want to continue? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 1
  fi
fi

# Navigate to the script directory
cd "$(dirname "$0")"

# First, stop the environment if it's running
if docker ps | grep -q "spark-"; then
  echo "\nStopping running Spark containers..."
  ./stop-environment.sh
  echo "\nWaiting for containers to stop..."
  sleep 5
fi

# If deep clean, remove everything including running containers
if [ "$DEEP_CLEAN" = true ]; then
  echo "\n=== Removing ALL containers (including running ones) ==="
  docker container stop $(docker container ls -aq) 2>/dev/null || true
  docker container rm $(docker container ls -aq) 2>/dev/null || true
  
  echo "\n=== Removing ALL images ==="
  docker rmi $(docker images -q) -f 2>/dev/null || true
  
  echo "\n=== Removing ALL networks ==="
  docker network rm $(docker network ls -q) 2>/dev/null || true
  
  echo "\n=== Removing ALL volumes ==="
  docker volume rm $(docker volume ls -q) 2>/dev/null || true
  
  echo "\n=== Removing ALL build cache ==="
  docker builder prune -af --filter until=336h
  # Remove dangling images (untagged images)
  docker image prune -f
else
  # Standard cleanup - only remove unused resources
  echo "\n=== Removing all stopped containers ==="
  docker container prune -f
  
  echo "\n=== Removing Apache Spark images ==="
  docker images | grep "apache-spark" | awk '{print $3}' | xargs -r docker rmi -f
  
  echo "\n=== Removing unused networks ==="
  docker network prune -f
  
  echo "\n=== Removing build cache ==="
  docker builder prune -f
  
  echo "\n=== Removing dangling images and build layers ==="
  # Remove dangling images (untagged images)
  docker image prune -f
  # Remove unused build cache
  docker buildx prune -f
  
  echo "\n=== Removing unused volumes ==="
  docker volume prune -f
fi

echo "\n=== Current Docker status ==="
echo "\nContainers:"
docker ps -a

echo "\nImages:"
docker images

echo "\nNetworks:"
docker network ls

echo "\nVolumes:"
docker volume ls

echo "\n=== Docker cleanup completed! ==="
if [ "$DEEP_CLEAN" = true ]; then
  echo "All Docker resources have been removed."
fi
echo "To rebuild the environment, run: ./build-images.sh"
echo "To start the environment, run: ./start-environment.sh"
echo "\nUsage:"
echo "  ./clean-docker.sh         # Standard cleanup (preserves running containers)"
echo "  ./clean-docker.sh --all   # Deep cleanup (removes ALL Docker resources)"
