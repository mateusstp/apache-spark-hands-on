FROM openjdk:11-jdk-slim

# Evitar interações durante a instalação
ARG DEBIAN_FRONTEND=noninteractive

# Definir variáveis de ambiente
ENV SPARK_VERSION=3.4.4
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.5-src.zip

# Instalação de dependências
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    wget \
    curl \
    procps \
    net-tools \
    rsync \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências do Python (separe as instalações para melhor caching)
RUN pip3 install --upgrade pip
RUN pip3 install pyspark==$SPARK_VERSION
RUN pip3 install findspark jupyter numpy pandas matplotlib
# Instalar dependências específicas para Spark Connect
RUN pip3 install pyarrow>=1.0.0 grpcio>=1.48.1 protobuf grpcio-status

# Baixar e configurar Apache Spark em uma única etapa para eficiência de camadas
RUN mkdir -p /opt/spark && \
    mkdir -p /opt/spark/logs && \
    mkdir -p /opt/spark/work && \
    wget -q https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz && \
    tar -xzf spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz -C /opt && \
    cp -r /opt/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION/* /opt/spark/ && \
    rm -rf /opt/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION && \
    rm spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz

# Expor portas para UI do Spark, Worker, Master e Jupyter
EXPOSE 4040 7077 8080 8088 8089 10000 18080

# Volume para persistência de dados
VOLUME ["/data"]

# Criar diretório de dados no container
RUN mkdir -p /data

# Configurações padrão do Spark
RUN echo "spark.master                     spark://spark-master:7077" >> $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.driver.host                spark-connect" >> $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.driver.bindAddress         0.0.0.0" >> $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.driver.memory              1g" >> $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.executor.memory            1g" >> $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.executor.cores             1" >> $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.sql.shuffle.partitions     4" >> $SPARK_HOME/conf/spark-defaults.conf && \
    # Configurações do Connect Server
    echo "spark.connect.grpc.binding.port  15002" >> $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.connect.grpc.binding.host  0.0.0.0" >> $SPARK_HOME/conf/spark-defaults.conf && \
    # Pacote necessário para o Connect Server
    echo "spark.jars.packages              org.apache.spark:spark-connect_2.12:3.4.4" >> $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.jars.ivy                   /tmp/.ivy" >> $SPARK_HOME/conf/spark-defaults.conf

# Diretório de trabalho
WORKDIR /opt/spark

# Copiar o script de inicialização
COPY start-spark-connect.sh /opt/spark/
RUN chmod +x /opt/spark/start-spark-connect.sh

# Criar um link simbólico para pip no diretório bin do Spark
RUN ln -s /usr/local/bin/pip3 /opt/spark/bin/pip

# Expor porta para Spark Connect
EXPOSE 15002

# Comando padrão para iniciar o Spark Connect Server
CMD ["/opt/spark/start-spark-connect.sh"]
