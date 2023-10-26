FROM postgres:16

RUN apt-get update && apt-get install -y postgresql-contrib git make gcc postgresql-server-dev-16 \
    && git clone https://github.com/eulerto/wal2json.git \
    && cd wal2json && make && make install \
    && cd .. && rm -rf wal2json
