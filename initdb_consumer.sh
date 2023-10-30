#!/bin/bash
psql -v ON_ERROR_STOP=1 --username postgres -d consumer  <<- EOSQL
    CREATE TABLE IF NOT EXISTS replication_positions (
       slot_name TEXT PRIMARY KEY,
       lsn INT NOT NULL
    );
EOSQL
