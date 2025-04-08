from pyspark.sql import SparkSession
from pyspark.sql import functions as func
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType
import sys
import os

def computeCosineSimilarity(spark, data):
    # Compute xx, xy and yy columns
    pairScores = data \
      .withColumn("xx", func.col("rating1") * func.col("rating1")) \
      .withColumn("yy", func.col("rating2") * func.col("rating2")) \
      .withColumn("xy", func.col("rating1") * func.col("rating2")) 

    # Compute numerator, denominator and numPairs columns
    calculateSimilarity = pairScores \
      .groupBy("movie1", "movie2") \
      .agg( \
        func.sum(func.col("xy")).alias("numerator"), \
        (func.sqrt(func.sum(func.col("xx"))) * func.sqrt(func.sum(func.col("yy")))).alias("denominator"), \
        func.count(func.col("xy")).alias("numPairs")
      )

    # Calculate score and select only needed columns (movie1, movie2, score, numPairs)
    result = calculateSimilarity \
      .withColumn("score", \
        func.when(func.col("denominator") != 0, func.col("numerator") / func.col("denominator")) \
          .otherwise(0) \
      ).select("movie1", "movie2", "score", "numPairs")

    return result

# Get movie name by given movie id 
def getMovieName(movieNames, movieId):
    result = movieNames.filter(func.col("movieID") == movieId) \
        .select("movieTitle").collect()[0]

    return result[0]


# Detectar ambiente (container vs. local)
# Verificar se os arquivos estão no caminho do container
try:
    if os.path.exists("/data/movielens/ml-100k/u.item"):
        # Executando dentro do container
        data_path = "/data/movielens/ml-100k"
        print("Executando dentro do container Docker, usando dados em: ", data_path)

        # Config para ambiente container - Usando Spark local
        print("Iniciando Spark em modo local dentro do container")
        spark = SparkSession.builder \
            .appName("MovieSimilarities") \
            .master("local[*]") \
            .getOrCreate()
    else:
        # Executando localmente (fora do container)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(os.path.dirname(script_dir), "data/movielens/ml-100k")
        print("Executando localmente, usando dados em: ", data_path)
        
        # Config para ambiente local - usando conexão remota via Spark Connect
        connect_url = "sc://localhost:15002"
        print(f"Conectando ao servidor Spark Connect em {connect_url}")
        
        try:
            # Verificar se as dependências estão instaladas
            import pandas as pd
            print(f"Pandas version: {pd.__version__}")
            
            import pyarrow
            print(f"PyArrow version: {pyarrow.__version__}")
            
            import grpc
            print(f"gRPC version: {grpc.__version__}")
            
            # Configuração para Spark Connect com tempo limite aumentado
            spark = SparkSession.builder \
                .remote(connect_url) \
                .config("spark.connect.timeout", "120s") \
                .config("spark.connect.connect.timeout", "120s") \
                .config("spark.connect.client.path.mapping.file:/Users/mateusos/Documents/projects/apache-spark/apache-spark-hands-on/apache-spark/data/movielens/ml-100k", "/data/movielens/ml-100k") \
                .appName("MovieSimilarities") \
                .getOrCreate()
            
            # Verificando se a conexão foi estabelecida
            print(f"Conexão estabelecida com Spark Connect. Versão do Spark: {spark.version}")
            
            # Ajustar o caminho para o caminho dentro do container
            data_path = "/data/movielens/ml-100k"
            print(f"Ajustando caminho para o caminho dentro do container: {data_path}")
            
        except ImportError as e:
            print(f"Erro de importação: {e}")
            print("Certifique-se de que todas as dependências estão instaladas: pandas, pyarrow, grpcio, protobuf")
            sys.exit(1)
        
    # Verificando o ambiente Spark
    print(f"Executando Spark versão: {spark.version}")

    # Removido: print(f"Modo de execução: {spark.sparkContext.master}")
    # sparkContext não é suportado no Spark Connect

except Exception as e:
    print(f"Erro ao inicializar Spark: {str(e)}")
    print("Verifique se o servidor Spark Connect está ativo na porta 15002")
    print("Executando diagnóstico de rede...")
    
    # Executar diagnóstico de rede para verificar a conexão
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(("localhost", 15002))
        if result == 0:
            print("Porta 15002 está aberta e acessível")
        else:
            print(f"Porta 15002 não está acessível (code: {result})")
        s.close()
    except Exception as net_error:
        print(f"Erro ao verificar conexão de rede: {net_error}")
    
    # Sugerir soluções
    print("\nSugestões para resolver o problema:")
    print("1. Confirme que o container Docker está em execução: docker ps")
    print("2. Verifique os logs do container: docker logs spark-connect")
    print("3. Verifique se a porta 15002 está mapeada corretamente no container")
    print("4. Tente acessar a interface web do Spark no navegador: http://localhost:8080")
    
    sys.exit(1)
    

movieNamesSchema = StructType([ \
                               StructField("movieID", IntegerType(), True), \
                               StructField("movieTitle", StringType(), True) \
                               ])
    
moviesSchema = StructType([ \
                     StructField("userID", IntegerType(), True), \
                     StructField("movieID", IntegerType(), True), \
                     StructField("rating", IntegerType(), True), \
                     StructField("timestamp", LongType(), True)])


# Create a broadcast dataset of movieID and movieTitle.
# Apply ISO-885901 charset
movieName_path = os.path.join(data_path, "u.item")
print(f"Lendo arquivo de nomes de filmes de: {movieName_path}")

movieName = spark.read \
      .option("sep", "|") \
      .option("charset", "ISO-8859-1") \
      .schema(movieNamesSchema) \
      .csv(movieName_path)

# Load up movie data as dataset
movies_path = os.path.join(data_path, "u.data")
print(f"Lendo arquivo de avaliações de filmes de: {movies_path}")

movies = spark.read \
      .option("sep", "\t") \
      .schema(moviesSchema) \
      .csv(movies_path)


ratings = movies.select("userId", "movieId", "rating")

# Emit every movie rated together by the same user.
# Self-join to find every combination.
# Select movie pairs and rating pairs
moviePairs = ratings.alias("ratings1") \
      .join(ratings.alias("ratings2"), (func.col("ratings1.userId") == func.col("ratings2.userId")) \
            & (func.col("ratings1.movieId") < func.col("ratings2.movieId"))) \
      .select(func.col("ratings1.movieId").alias("movie1"), \
        func.col("ratings2.movieId").alias("movie2"), \
        func.col("ratings1.rating").alias("rating1"), \
        func.col("ratings2.rating").alias("rating2"))


moviePairSimilarities = computeCosineSimilarity(spark, moviePairs).cache()

if (len(sys.argv) > 1):
    scoreThreshold = 0.97
    coOccurrenceThreshold = 50.0

    movieID = int(sys.argv[1])

    # Filter for movies with this sim that are "good" as defined by
    # our quality thresholds above
    filteredResults = moviePairSimilarities.filter( \
        ((func.col("movie1") == movieID) | (func.col("movie2") == movieID)) & \
          (func.col("score") > scoreThreshold) & (func.col("numPairs") > coOccurrenceThreshold))

    # Sort by quality score.
    results = filteredResults.sort(func.col("score").desc()).take(10)
    
    print ("Top 10 similar movies for " + getMovieName(movieName, movieID))
    
    for result in results:
        # Display the similarity result that isn't the movie we're looking at
        similarMovieID = result.movie1
        if (similarMovieID == movieID):
          similarMovieID = result.movie2
        
        print(getMovieName(movieName, similarMovieID) + "\tscore: " \
              + str(result.score) + "\tstrength: " + str(result.numPairs))
else:
    print("Por favor, forneça um ID de filme como argumento de linha de comando")
