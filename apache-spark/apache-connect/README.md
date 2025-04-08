# Apache Spark Movie Similarities with Spark Connect

This directory contains a Docker environment for running movie similarity analysis using Apache Spark Connect, which allows you to run Python code locally while processing data in a Spark cluster.

## Project Structure

- `Dockerfile`: Apache Spark environment configuration
- `docker-compose.yml`: Spark services configuration (master, workers, connect)
- `movie-similarities-local.py`: Script to analyze movie similarities via Spark Connect
- `test_connection.py`: Simple script to test the connection with Spark Connect
- `requirements.txt`: Dependencies for the Docker environment
- `requirements-local.txt`: Dependencies for the local environment
- `start-environment.sh`: Script to start the Docker environment
- `build-images.sh`: Script to build Docker images
- `stop-environment.sh`: Script to stop the Docker environment
- `clean-docker.sh`: Script to clean Docker resources (containers, images, networks, volumes)

## Prerequisites

- Docker and Docker Compose installed on your system
- Python 3.x installed locally

## Setting Up the Environment

### 1. Build and Start Docker Services

You can use the provided automation scripts:

```bash
# Navigate to the apache-connect directory
cd apache-spark/apache-connect

# Build the Docker images (only needed once or when Dockerfile changes)
./build-images.sh

# Start the environment
./start-environment.sh
```

Or manually with Docker Compose:

```bash
# Build the Docker image and start services
docker-compose up -d --build
```

### 2. Configure the Local Python Environment

```bash
# Create and activate Python virtual environment
python -m venv spark-venv
source spark-venv/bin/activate  # On Windows: spark-venv\Scripts\activate

# Install dependencies
pip install -r requirements-local.txt
```

## Running the Movie Similarity Analysis

The `movie-similarities-local.py` script runs **locally** but connects to the Spark Connect server to process the data.

```bash
# Activate the virtual environment (if not already activated)
source spark-venv/bin/activate

# Run the script with a movie ID as an argument
python movie-similarities-local.py 50
```

This will analyze movie similarities and return recommendations for the movie with ID 50 (Star Wars). You can replace 50 with any other movie ID you want.

### Testing the Connection

To verify if the connection with Spark Connect is working:

```bash
python test_connection.py
```

## Monitoring the Spark Application

With the services running, you can access:

- Spark Master Web UI: http://localhost:8080
- Spark Connect Web UI: http://localhost:4040 (during application execution)

## Stopping the Services

Using the automation script:

```bash
# Stop all services
./stop-environment.sh
```

Or manually with Docker Compose:

```bash
# Stop all services
docker-compose down
```

## Cleaning Docker Resources

To clean up Docker resources after using the environment, you can use the provided script:

```bash
# Standard cleanup (preserves running containers)
./clean-docker.sh

# Deep cleanup (removes ALL Docker resources, including running containers)
./clean-docker.sh --all
```

The cleanup script will remove:
- Stopped containers
- Apache Spark images
- Unused networks
- Build cache
- Unused volumes

The deep cleanup mode (--all) will remove ALL Docker resources, including running containers from other projects.

## Troubleshooting

If you encounter connection issues:

1. Check if all services are running: `docker-compose ps`
2. Check the Spark Connect service logs: `docker-compose logs spark-connect`
3. Make sure port 15002 is accessible locally
4. Verify that Python dependencies are correctly installed in the virtual environment

## Additional Notes

- The data directory is automatically mounted in the container via docker-compose
- The path `/data` inside the container is configured to access the data
- For large datasets, consider increasing the memory allocated to Spark executors by modifying the parameters in docker-compose.yml
