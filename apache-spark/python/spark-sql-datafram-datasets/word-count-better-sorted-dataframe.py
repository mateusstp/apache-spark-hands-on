import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as func

BASE_DIR = os.path.join(os.getcwd().split('python')[0], 'data')
DATA_FILE = os.path.join(BASE_DIR, 'book.txt')

spark = SparkSession.builder.appName("WordCount").getOrCreate()

# Read each line of my book into a dataframe
inputDF = spark.read.text(DATA_FILE)

# Split using a regular expression that extracts words
words = inputDF.select(func.explode(func.split(inputDF.value, "\\W+")).alias("word"))
wordsWithoutEmptyString = words.filter(words.word != "")

# Normalize everything to lowercase
lowercaseWords = wordsWithoutEmptyString.select(func.lower(wordsWithoutEmptyString.word).alias("word"))

# Count up the occurrences of each word
wordCounts = lowercaseWords.groupBy("word").count()

# Sort by counts
wordCountsSorted = wordCounts.sort("count")

# Show the results.
wordCountsSorted.show(wordCountsSorted.count())
