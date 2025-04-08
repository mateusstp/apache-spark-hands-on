#!/bin/bash

# Script para iniciar o servidor Spark Connect

echo "Iniciando Spark Connect Server..."

# Verificar se o pacote do Spark Connect está disponível
if [ -z "$SPARK_HOME" ]; then
  echo "SPARK_HOME não está definido. Abortando."
  exit 1
fi

# Iniciar o servidor Spark Connect
echo "Iniciando o servidor Spark Connect na porta 15002..."
$SPARK_HOME/sbin/start-connect-server.sh \
  --packages org.apache.spark:spark-connect_2.12:$SPARK_VERSION \
  --conf spark.connect.grpc.binding.port=15002 \
  --conf spark.connect.grpc.binding.host=0.0.0.0

# Manter o container em execução
tail -f $SPARK_HOME/logs/*
