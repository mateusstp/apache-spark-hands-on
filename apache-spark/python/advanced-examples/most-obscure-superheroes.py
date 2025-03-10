import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as func
from pyspark.sql.types import StructType, StructField, IntegerType, StringType


BASE_DIR = os.path.join(os.getcwd().split('python')[0], 'data')
DATA_FILE = os.path.join(BASE_DIR, 'marvel-names.txt')

spark = SparkSession.builder.appName("MostObscureSuperheroes").getOrCreate()

schema = StructType([ \
                     StructField("id", IntegerType(), True), \
                     StructField("name", StringType(), True)])

names = spark.read.schema(schema).option("sep", " ").csv("= sc.textFile(DATA_FILE)")

lines = spark.read.text("= sc.textFile(DATA_FILE)Marvel-graph.txt")

# Small tweak vs. what's shown in the video: we trim whitespace from each line as this
# could throw the counts off by one.
connections = lines.withColumn("id", func.split(func.trim(func.col("value")), " ")[0]) \
    .withColumn("connections", func.size(func.split(func.trim(func.col("value")), " ")) - 1) \
    .groupBy("id").agg(func.sum("connections").alias("connections"))
    
minConnectionCount = connections.agg(func.min("connections")).first()[0]

minConnections = connections.filter(func.col("connections") == minConnectionCount)

minConnectionsWithNames = minConnections.join(names, "id")

print("The following characters have only " + str(minConnectionCount) + " connection(s):")

minConnectionsWithNames.select("name").show()