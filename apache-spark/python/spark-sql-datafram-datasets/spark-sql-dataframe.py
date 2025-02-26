import os
from pyspark.sql import SparkSession

BASE_DIR = os.path.join(os.getcwd().split('python')[0], 'data')
DATA_FILE = os.path.join(BASE_DIR, 'fakefriends-header.csv')

spark = SparkSession.builder.appName("SparkSQL").getOrCreate()

people = spark.read.option("header", "true").option("inferSchema", "true")\
    .csv(DATA_FILE)
    
print("Here is our inferred schema:")
people.printSchema()

print("Let's display the name column:")
people.select("name").show()

print("Filter out anyone over 21:")
people.filter(people.age < 21).show()

print("Group by age")
people.groupBy("age").count().show()

print("Make everyone 10 years older:")
people.select(people.name, people.age + 10).show()

spark.stop()

