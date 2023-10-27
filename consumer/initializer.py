from typing import NoReturn

import psycopg2
import psycopg2.extras

from config import consumer_settings, producer_settings
from consumer.ddl import DDLExtractor


class Initializer:
    
    def __init__(self, table_names: list[str]) -> None:
        self.table_names = table_names
    
    def run(self) -> NoReturn:
        ddl = self._extract_ddl(self.table_names)
        self._create_tables(ddl)
        print("Done!")
    
    @staticmethod
    def _extract_ddl(table_names: list[str]) -> list[str]:
        print("Connecting to producer database...")
        print("Extracting DDL...")
        with psycopg2.connect(producer_settings.get_connection_string()) as connection:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            ddl_operations = []
            for table_name in table_names:
                ddl_operations.append(DDLExtractor(cursor, table_name).extract())
        return ddl_operations
    
    @staticmethod
    def _create_tables(ddl: list[str]) -> None:
        print("Connecting to consumer database...")
        with psycopg2.connect(consumer_settings.get_connection_string()) as connection:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            print("Creating tables...")
            for ddl_operation in ddl:
                cursor.execute(ddl_operation)
            connection.commit()
