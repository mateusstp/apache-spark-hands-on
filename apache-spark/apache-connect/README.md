# Apache Spark Movie Similarities - Docker Setup

This directory contains a Docker environment for running movie similarity analysis using Apache Spark, along with a Python script for demonstration.

## Project Structure

- `Dockerfile`: Apache Spark environment configuration
- `movie-similarities-dataframe-connect.py`: Script for analyzing movie similarities

## Prerequisites

- Docker installed on your system
- Git to clone the repository (if you haven't already)

## Building the Docker Image

To build the Docker image with the Apache Spark environment:

```bash
# Navigate to the apache-connect directory
cd apache-spark/apache-connect

# Build the Docker image
docker build -t apache-spark-movies:latest .
```

## Running the Container

There are two ways to run the container:

### Method 1: Interactive Execution

```bash
# Run the container interactively with data volume mount
docker run -it --name spark-movies -p 4040:4040 -p 8080:8080 -v "$(pwd)/../data:/data" apache-spark-movies:latest
```

### Method 2: Background Execution

```bash
# Run the container in the background with data volume mount
docker run -d --name spark-movies -p 4040:4040 -p 8080:8080 -v "$(pwd)/../data:/data" apache-spark-movies:latest /opt/spark/bin/spark-class org.apache.spark.deploy.master.Master
```

## Running the Analysis Script

The script `movie-similarities-dataframe-connect.py` needs to be executed **inside the container** because it depends on the file paths that exist in the container's filesystem.

```bash
# Copy the script to the container
docker cp movie-similarities-dataframe-connect.py spark-movies:/opt/spark/

# Execute the script inside the container
docker exec -it spark-movies /bin/bash -c "cd /opt/spark && spark-submit movie-similarities-dataframe-connect.py 50"
```

This will analyze movie similarities and return recommendations for movie ID 50. You can replace 50 with any other movie ID you're interested in.

### Accessing the Spark Web UI

During script execution, you can access the Spark UI at http://localhost:4040 (or 4041 if 4040 is already in use).

## Monitoring the Spark Application

Once the application is running, you can access:

- Spark UI: http://localhost:4040 (during application execution)
- Spark Master UI: http://localhost:8080 (cluster overview)

## Stopping the Container

```bash
# Stop the container
docker stop spark-movies

# Remove the container
docker rm spark-movies
```

## Additional Notes

- You need to mount your data directory as a volume when running the container using the `-v` flag as shown in the examples above.
- The path `/data` inside the container is created and ready to use with your mounted data.
- For large datasets, consider increasing the memory allocated to Spark executors by modifying the `spark.executor.memory` parameter.
