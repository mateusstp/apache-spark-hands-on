#!/bin/bash

# Número de workers a serem iniciados (padrão: 2, pode ser sobrescrito pela variável de ambiente SPARK_WORKERS)
NUM_WORKERS=${SPARK_WORKERS:-2}

# Memória por worker (padrão: 1g, pode ser sobrescrito pela variável de ambiente SPARK_WORKER_MEMORY)
WORKER_MEMORY=${SPARK_WORKER_MEMORY:-1g}

# Cores por worker (padrão: 1, pode ser sobrescrito pela variável de ambiente SPARK_WORKER_CORES)
WORKER_CORES=${SPARK_WORKER_CORES:-1}

echo "Configuração do Spark:"
echo "- Número de workers: $NUM_WORKERS"
echo "- Memória por worker: $WORKER_MEMORY"
echo "- Cores por worker: $WORKER_CORES"

# Iniciar o Spark Master
/opt/spark/sbin/start-master.sh

# Aguardar o Master iniciar
sleep 5

# Iniciar múltiplos Workers e conectar ao Master
for ((i=1; i<=$NUM_WORKERS; i++))
do
    echo "Iniciando worker $i..."
    /opt/spark/sbin/start-worker.sh \
        --memory $WORKER_MEMORY \
        --cores $WORKER_CORES \
        spark://$(hostname):7077
    sleep 2
done

# Aguardar os Workers iniciarem
sleep 5

echo "Iniciando Spark Connect Server na porta 15002..."

# Criar arquivo de configuração Spark para o servidor Connect
cat > /opt/spark/conf/spark-defaults.conf << EOF
spark.master=spark://$(hostname):7077
spark.driver.bindAddress=0.0.0.0
spark.driver.host=$(hostname)
spark.connect.grpc.binding.port=15002
spark.connect.grpc.binding.host=0.0.0.0
EOF

# Criar script Python para servidor Spark Connect
cat > /opt/spark/connect_server.py << EOF
from pyspark.sql import SparkSession
import time
import os
import sys

print("Iniciando servidor Spark Connect...")

# Configurar a sessão Spark com recursos aumentados
spark = SparkSession.builder \
    .appName("SparkConnectServer") \
    .config("spark.master", "spark://$(hostname):7077") \
    .config("spark.ui.port", "4040") \
    .config("spark.connect.enabled", "true") \
    .config("spark.connect.grpc.binding.port", "15002") \
    .config("spark.connect.grpc.binding.host", "0.0.0.0") \
    .config("spark.driver.bindAddress", "0.0.0.0") \
    .config("spark.driver.memory", "${SPARK_DRIVER_MEMORY:-1g}") \
    .config("spark.executor.memory", "${SPARK_EXECUTOR_MEMORY:-1g}") \
    .config("spark.executor.cores", "${SPARK_EXECUTOR_CORES:-1}") \
    .config("spark.executor.instances", "${NUM_WORKERS:-2}") \
    .config("spark.default.parallelism", "${SPARK_DEFAULT_PARALLELISM:-4}") \
    .config("spark.sql.shuffle.partitions", "${SPARK_SHUFFLE_PARTITIONS:-4}") \
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

# Iniciar o servidor Spark Connect
/opt/spark/bin/spark-submit \
  --master spark://$(hostname):7077 \
  --packages org.apache.spark:spark-connect_2.12:3.4.4 \
  --conf spark.jars.ivy=/tmp/.ivy \
  /opt/spark/connect_server.py &

# Aguardar o servidor iniciar
sleep 10

# Verificar se a porta está escutando
echo "Verificando porta 15002..."
netstat -tuln | grep 15002 || echo "Porta 15002 não está sendo escutada!"

echo "Spark Connect Server iniciado na porta 15002"

# Manter o container rodando e mostrar logs
tail -f /opt/spark/logs/*
