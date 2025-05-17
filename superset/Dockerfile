FROM apache/superset:latest

USER root

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libssl-dev \
    pkg-config \
 && pip install mysqlclient \
 && pip install psycopg2 \
 && apt-get remove -y build-essential pkg-config \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

USER superset
