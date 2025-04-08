import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as func, Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, FloatType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.join(os.getcwd().split('python')[0], 'data')
DATA_ITEM = os.path.join(BASE_DIR, 'movielens/ml-100k', 'u.item')
DATA_FILE = os.path.join(BASE_DIR, 'movielens/ml-100k', 'u.data')

# Function to configure Spark session
def configure_spark(app_name="MovieSimilarities", driver_memory="8g", executor_memory="1g"):
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.driver.memory", driver_memory) \
        .config("spark.executor.memory", executor_memory) \
        .getOrCreate()

# Function to load data
def load_data(spark, item_path, data_path):
    movieNamesSchema = StructType([
        StructField("movieID", IntegerType(), True),
        StructField("movieTitle", StringType(), True)
    ])
    moviesSchema = StructType([
        StructField("userID", IntegerType(), True),
        StructField("movieID", IntegerType(), True),
        StructField("rating", IntegerType(), True),
        StructField("timestamp", LongType(), True)
    ])
    
    movieNames = spark.read \
        .option("sep", "|") \
        .option("charset", "ISO-8859-1") \
        .schema(movieNamesSchema) \
        .csv(item_path)
    
    movies = spark.read \
        .option("sep", "\t") \
        .schema(moviesSchema) \
        .csv(data_path)
    
    return movieNames, movies

# Function to calculate Jaccard similarity
def calculate_jaccard_similarity(movies):
    ratings = movies.select("userID", "movieID", "rating")
    moviePairs = ratings.alias('ratings1').join(ratings.alias('ratings2'), \
        (func.col('ratings1.movieID') > func.col('ratings2.movieID')) & (func.col('ratings1.userID') == func.col('ratings2.userID')), "left")
    moviePairs = moviePairs.select(
        func.col("ratings1.movieID").alias("movie1"),
        func.col("ratings2.movieID").alias("movie2"),
        func.col("ratings1.rating").alias("rating1"),
        func.col("ratings2.rating").alias("rating2")
    )
    movieSet = moviePairs.select("movie1", "movie2") \
        .groupBy("movie1").agg(func.collect_set(func.col("movie2")).alias("movies"))
    moviesSet = moviePairs.distinct().alias('MP') \
        .join(movieSet.alias('MS'), func.col('MP.movie1') == func.col('MS.movie1'), "left") \
        .join(movieSet.alias('MS2'), func.col('MP.movie2') == func.col('MS2.movie1'), "left") \
        .select(func.col("MP.movie1").alias("movie1"), func.col("MP.movie2").alias("movie2"), func.col("MS.movies").alias("movies1"), func.col("MS2.movies").alias("movies2"))
    
    jaccardSchema = StructType([
        StructField("movie1", IntegerType(), True),
        StructField("movie2", IntegerType(), True),
        StructField("jaccard_similarity", FloatType(), True)
    ])
    
    def jaccard_similarity(row):
        movie1, movie2, movies1, movies2 = row
        return Row(movie1=movie1, movie2=movie2, jaccard_similarity=len(set(movies1) & set(movies2)) / len(set(movies1) | set(movies2)))
    
    movieJaccard = moviesSet.rdd.map(jaccard_similarity)
    return SparkSession.builder.getOrCreate().createDataFrame(movieJaccard, jaccardSchema)

# Function to get top similar movies
def get_top_similar_movies(dfMovieJaccard, movieNames, movieID, scoreThreshold):
    results = dfMovieJaccard.where(f"( movie1 = {movieID} OR movie2 = {movieID}) AND jaccard_similarity > {scoreThreshold}") \
        .orderBy(func.desc(func.col("jaccard_similarity"))).limit(10).collect()
    logging.info(f"Top 10 similar movies for {getMovieName(movieNames, movieID)}")
    for result in results:
        similarMovieID = result.movie1
        if (similarMovieID == movieID):
            similarMovieID = result.movie2
        logging.info(f"{getMovieName(movieNames, similarMovieID)}\tscore: {result.jaccard_similarity}")

# Function to get movie name by given movie id 
def getMovieName(movieNames, movieId):
    result = movieNames.filter(func.col("movieID") == movieId) \
        .select("movieTitle").collect()[0]
    return result[0]

# Main execution block
def main():
    try:
        spark = configure_spark()
        movieNames, movies = load_data(spark, DATA_ITEM, DATA_FILE)
        dfMovieJaccard = calculate_jaccard_similarity(movies)
        dfMovieJaccard.cache()
        movieID = 50
        scoreThreshold = 0.90
        get_top_similar_movies(dfMovieJaccard, movieNames, movieID, scoreThreshold)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()