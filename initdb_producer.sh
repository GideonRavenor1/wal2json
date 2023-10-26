#!/bin/bash
psql -v ON_ERROR_STOP=1 --username postgres -d producer <<-EOSQL
     CREATE TABLE IF NOT EXISTS test_1 (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL
     );
    CREATE TABLE IF NOT EXISTS test_2 (
        id SERIAL PRIMARY KEY,
        email VARCHAR(100) NOT NULL
     );
    CREATE TABLE IF NOT EXISTS test_3 (
        id SERIAL PRIMARY KEY,
        number INT NOT NULL
     );
EOSQL