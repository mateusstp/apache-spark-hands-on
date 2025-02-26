import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as func
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

BASE_DIR = os.path.join(os.getcwd().split('python')[0], 'data')
DATA_FILE_NAME = os.path.join(BASE_DIR, 'marvel-names.txt')
DATA_FILE_GRAPTH = os.path.join(BASE_DIR, 'marvel-graph.txt')

spark = SparkSession.builder.appName("MostPopularSuperhero").getOrCreate()

schema = StructType([ \
                     StructField("id", IntegerType(), True), \
                     StructField("name", StringType(), True)])

names = spark.read.schema(schema).option("sep", " ").csv(DATA_FILE_NAME)

lines = spark.read.text(DATA_FILE_GRAPTH)

# Small tweak vs. what's shown in the video: we trim each line of whitespace as that could
# throw off the counts.
connections = lines.withColumn("id", func.split(func.trim(func.col("value")), " ")[0]) \
    .withColumn("connections", func.size(func.split(func.trim(func.col("value")), " ")) - 1) \
    .groupBy("id").agg(func.sum("connections").alias("connections"))
    
mostPopular = connections.sort(func.col("connections").desc()).first()

mostPopularName = names.filter(func.col("id") == mostPopular[0]).select("name").first()


print("\n >>>>>>> " + mostPopularName[0] + " is the most popular superhero with " + str(mostPopular[1]) + " co-appearances.\n\n")

