# check=skip=SecretsUsedInArgOrEnv
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV REDIS_USERNAME=redis
ENV REDIS_PASSWORD=redis
ENV NEO4J_USERNAME=neo4j
ENV NEO4J_PASSWORD=neo4j

# ==============================
# Installazione pacchetti base
# ==============================
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    lsb-release \
    openjdk-17-jre \
    unzip \
    apt-transport-https \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# ==============================
# Installazione Redis
# ==============================
RUN apt-get update && apt-get install -y redis-server && rm -rf /var/lib/apt/lists/*

# Configurazione Redis con username/password
RUN mkdir -p /etc/redis && \
    echo "port 6379" > /etc/redis/redis.conf && \
    echo "protected-mode yes" >> /etc/redis/redis.conf && \
    echo "requirepass ${REDIS_PASSWORD}" >> /etc/redis/redis.conf && \
    echo "user ${REDIS_USERNAME} on +${REDIS_PASSWORD} ~* +@all" >> /etc/redis/redis.conf

EXPOSE 6379

# ==============================
# Installazione Neo4j Community
# ==============================
RUN wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - \
    && echo "deb https://debian.neo4j.com stable 5" > /etc/apt/sources.list.d/neo4j.list \
    && apt-get update && apt-get install -y neo4j=1:5.23.0 \
    && rm -rf /var/lib/apt/lists/*

# Configura username e password Neo4j
RUN sed -i 's/#dbms.default_listen_address=0.0.0.0/dbms.default_listen_address=0.0.0.0/' /etc/neo4j/neo4j.conf \
    && echo "dbms.security.auth_enabled=true" >> /etc/neo4j/neo4j.conf

ENV NEO4J_AUTH=${NEO4J_USERNAME}/${NEO4J_PASSWORD}

EXPOSE 7474 7687

# ==============================
# Installazione Qdrant
# ==============================
RUN wget https://github.com/qdrant/qdrant/releases/download/v1.15.1/qdrant_1.15.1-1_amd64.deb \
    && dpkg -i qdrant_1.15.1-1_amd64.deb \
    && rm qdrant_1.15.1-1_amd64.deb
EXPOSE 6333

# ==============================
# Installazione Grafana
# ==============================
RUN wget -q -O - https://packages.grafana.com/gpg.key | apt-key add - \
    && add-apt-repository "deb https://packages.grafana.com/oss/deb stable main" \
    && apt-get update && apt-get install -y grafana \
    && rm -rf /var/lib/apt/lists/*
EXPOSE 3000

# ==============================
# Installazione Loki
# ==============================
RUN wget https://github.com/grafana/loki/releases/latest/download/loki-linux-amd64.zip \
    && unzip loki-linux-amd64.zip \
    && mv loki-linux-amd64 /usr/local/bin/loki \
    && chmod +x /usr/local/bin/loki \
    && rm loki-linux-amd64.zip
EXPOSE 3100

# ==============================
# Script di avvio per tutti i servizi
# ==============================
RUN echo '#!/bin/bash\n\
redis-server /etc/redis/redis.conf --daemonize yes\n\
neo4j start\n\
qdrant &\n\
/usr/sbin/grafana-server --homepath=/usr/share/grafana &\n\
loki --config.file=/etc/loki/local-config.yaml &\n\
tail -f /dev/null' > /start.sh \
    && chmod +x /start.sh

CMD ["/start.sh"]
