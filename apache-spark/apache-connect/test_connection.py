from pyspark.sql import SparkSession

# Connect to Spark Connect server
spark = SparkSession.builder \
    .remote("sc://localhost:15002") \
    .appName("SparkConnectTest") \
    .getOrCreate()

# Create a simple DataFrame
df = spark.createDataFrame([(1, 'Alice'), (2, 'Bob')], ['id', 'name'])

# Show the DataFrame
df.show()

# Execute a simple SQL operation
df.createOrReplaceTempView("people")
result = spark.sql("SELECT * FROM people WHERE id = 1")
result.show()

# Stop the session
spark.stop()
