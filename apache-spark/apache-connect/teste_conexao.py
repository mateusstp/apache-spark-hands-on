from pyspark.sql import SparkSession

# Conecta ao servidor Spark Connect
spark = SparkSession.builder \
    .remote("sc://localhost:15002") \
    .appName("TesteConexaoDentroContainer") \
    .getOrCreate()

# Cria um DataFrame simples
df = spark.createDataFrame([(1, 'Alice'), (2, 'Bob')], ['id', 'name'])

# Mostra o DataFrame
df.show()

# Executa uma operação SQL simples
df.createOrReplaceTempView("people")
result = spark.sql("SELECT * FROM people WHERE id = 1")
result.show()

# Finaliza a sessão
spark.stop()
