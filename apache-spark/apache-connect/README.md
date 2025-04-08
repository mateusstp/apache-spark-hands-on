# Apache Spark Movie Similarities com Spark Connect

Este diretu00f3rio contu00e9m um ambiente Docker para executar anu00e1lise de similaridade de filmes usando Apache Spark Connect, que permite executar cu00f3digo Python localmente enquanto processa dados em um cluster Spark.

## Estrutura do Projeto

- `Dockerfile`: Configurau00e7u00e3o do ambiente Apache Spark
- `docker-compose.yml`: Configurau00e7u00e3o dos serviu00e7os Spark (master, workers, connect)
- `movie-similarities-local.py`: Script para analisar similaridades de filmes via Spark Connect
- `teste_conexao.py`: Script simples para testar a conexu00e3o com o Spark Connect
- `requirements.txt`: Dependu00eancias para o ambiente Docker
- `requirements-local.txt`: Dependu00eancias para o ambiente local

## Pru00e9-requisitos

- Docker e Docker Compose instalados no seu sistema
- Python 3.x instalado localmente

## Configurando o Ambiente

### 1. Construir e Iniciar os Serviu00e7os Docker

```bash
# Navegar para o diretu00f3rio apache-connect
cd apache-spark/apache-connect

# Construir a imagem Docker e iniciar os serviu00e7os
docker-compose up -d --build
```

### 2. Configurar o Ambiente Python Local

```bash
# Criar e ativar ambiente virtual Python
python -m venv spark-venv
source spark-venv/bin/activate  # No Windows: spark-venv\Scripts\activate

# Instalar dependu00eancias
pip install -r requirements-local.txt
```

## Executando a Anu00e1lise de Similaridade de Filmes

O script `movie-similarities-local.py` u00e9 executado **localmente** mas se conecta ao servidor Spark Connect para processar os dados.

```bash
# Ativar o ambiente virtual (se ainda nu00e3o estiver ativado)
source spark-venv/bin/activate

# Executar o script com um ID de filme como argumento
python movie-similarities-local.py 50
```

Isso analisaru00e1 as similaridades de filmes e retornaru00e1 recomendau00e7u00f5es para o filme com ID 50 (Star Wars). Vocu00ea pode substituir 50 por qualquer outro ID de filme que desejar.

### Testando a Conexu00e3o

Para verificar se a conexu00e3o com o Spark Connect estu00e1 funcionando:

```bash
python teste_conexao.py
```

## Monitorando a Aplicau00e7u00e3o Spark

Com os serviu00e7os em execuu00e7u00e3o, vocu00ea pode acessar:

- Interface Web do Spark Master: http://localhost:8080
- Interface Web do Spark Connect: http://localhost:4040 (durante a execuu00e7u00e3o da aplicau00e7u00e3o)

## Parando os Serviu00e7os

```bash
# Parar todos os serviu00e7os
docker-compose down
```

## Soluu00e7u00e3o de Problemas

Se encontrar problemas de conexu00e3o:

1. Verifique se todos os serviu00e7os estu00e3o em execuu00e7u00e3o: `docker-compose ps`
2. Verifique os logs do serviu00e7o Spark Connect: `docker-compose logs spark-connect`
3. Certifique-se de que a porta 15002 estu00e1 acessu00edvel localmente
4. Verifique se as dependu00eancias Python estu00e3o instaladas corretamente no ambiente virtual

## Notas Adicionais

- O diretu00f3rio de dados u00e9 montado automaticamente no container via docker-compose
- O caminho `/data` dentro do container estu00e1 configurado para acessar os dados
- Para conjuntos de dados grandes, considere aumentar a memu00f3ria alocada para os executores Spark modificando os paru00e2metros no docker-compose.yml
