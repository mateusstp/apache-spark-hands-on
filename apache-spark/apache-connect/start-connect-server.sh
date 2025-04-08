#!/bin/bash

echo "Iniciando servidor Spark Connect..."

# Aguardar um tempo para garantir que o Master esteja pronto
sleep 10

# Criar o arquivo do servidor Spark Connect
cat > /opt/spark/connect_server.py << 'EOF'
from pyspark.sql import SparkSession
import time
import os
import sys

print("Iniciando servidor Spark Connect...")

# Configurar a sessão Spark com recursos aumentados
# Garantir que o servidor Spark Connect esteja escutando em todas as interfaces
spark = SparkSession.builder \
    .appName("SparkConnectServer") \
    .config("spark.master", "spark://spark-master:7077") \
    .config("spark.ui.port", "4040") \
    .config("spark.connect.enabled", "true") \
    .config("spark.connect.grpc.binding.port", "15002") \
    .config("spark.connect.grpc.binding.host", "0.0.0.0") \
    .config("spark.driver.bindAddress", "0.0.0.0") \
    .config("spark.driver.host", "spark-connect") \
    .config("spark.driver.memory", os.environ.get("SPARK_DRIVER_MEMORY", "2g")) \
    .config("spark.executor.memory", os.environ.get("SPARK_EXECUTOR_MEMORY", "1g")) \
    .config("spark.executor.cores", os.environ.get("SPARK_EXECUTOR_CORES", "2")) \
    .config("spark.default.parallelism", os.environ.get("SPARK_DEFAULT_PARALLELISM", "8")) \
    .config("spark.sql.shuffle.partitions", os.environ.get("SPARK_SHUFFLE_PARTITIONS", "8")) \
    .getOrCreate()

print(f"Spark Connect Server iniciado na porta 15002. Versão Spark: {spark.version}")

# Criar algum dado de exemplo para confirmar que a sessão está funcionando
try:
    # Criar um DataFrame de exemplo
    data = [(1, "spark"), (2, "connect")]
    df = spark.createDataFrame(data, ["id", "name"])
    count = df.count()
    print(f"DataFrame de teste criado com {count} linhas")
    print("Spark session foi configurada com sucesso")
except Exception as e:
    print(f"Erro ao criar DataFrame de teste: {e}")

# Manter o servidor alive
while True:
    time.sleep(60)
    # Mostrar status para evitar que o processo seja morto por inatividade
    print("Spark Connect server continua em execução...")
EOF

# Executar o servidor Spark Connect com configurações explícitas para binding
# Forçar o uso de IPv4 e desabilitar IPv6
/opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-connect_2.12:3.4.4 \
  --conf spark.connect.grpc.binding.port=15002 \
  --conf spark.connect.grpc.binding.host=0.0.0.0 \
  --conf spark.driver.host=spark-connect \
  --conf spark.driver.bindAddress=0.0.0.0 \
  --conf spark.jars.ivy=/tmp/.ivy \
  --driver-java-options="-Djava.net.preferIPv4Stack=true -Djava.net.preferIPv4Addresses=true" \
  /opt/spark/connect_server.py
