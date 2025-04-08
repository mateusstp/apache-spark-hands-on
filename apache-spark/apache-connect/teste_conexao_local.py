from pyspark.sql import SparkSession
import sys

try:
    print("Conectando ao servidor Spark Connect via localhost:15002...")
    
    # Configuração para Spark Connect - versão local
    # Usamos localhost pois estamos executando fora do Docker
    spark = SparkSession.builder \
        .remote("sc://localhost:15002") \
        .appName("TesteConexao") \
        .getOrCreate()
    
    # Testa a conexão com uma operação simples
    df = spark.range(1, 10)
    count = df.count()
    print(f"Conexão bem-sucedida! Contagem: {count}")
    print(f"Versão do Spark: {spark.version}")
    print(f"Modo de execução: {spark.sparkContext.master}")
    
    # Finaliza a sessão
    spark.stop()
    print("Teste concluído com sucesso!")
    
except Exception as e:
    print(f"Erro ao conectar ao Spark: {str(e)}")
    sys.exit(1)
