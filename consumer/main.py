import sys
from typing import NoReturn

import psycopg2
import psycopg2.extras
from psycopg2 import sql
from psycopg2.errors import DuplicateObject
from psycopg2.extensions import connection as Connection, cursor as Cursor
from psycopg2.extras import LogicalReplicationConnection, ReplicationCursor

from config import consumer_settings, producer_settings
from consumer.callback import Callback
from consumer.initializer import Initializer

TABLE_NAMES = ['test_1', 'test_2', 'test_3']
REPLICATION_SLOT_NAME = 'wal2json_slot'
PLAGIN_NAME = 'wal2json'


class Customer:
    
    def start_consume(self) -> NoReturn:
        consumer_connection = self._get_consumer_connection()
        consumer_cursor = self._get_consumer_cursor(consumer_connection)
        
        producer_connection = self._get_producer_connection()
        producer_cursor = self._get_producer_cursor(producer_connection)
        
        self._create_producer_replication(producer_cursor)
        
        start_lsn = self._get_start_lsn(consumer_cursor)
        self._start_producer_replication(producer_cursor, start_lsn)
        
        try:
            print(f"Starting replication stream at LSN `{start_lsn}`")
            self._consume_stream(producer_cursor, consumer_connection, consumer_cursor)
        except KeyboardInterrupt:
            print("Stopping replication stream...")
        except Exception as e:
            print("Unexpected error:", e)
        finally:
            # Сохраняем текущую позицию LSN после остановки чтения
            lsn = producer_cursor.wal_end
            print(f"Saving current LSN `{lsn}`")
            self._save_start_lsn(lsn, consumer_cursor)
            consumer_connection.commit()
            
            consumer_cursor.close()
            consumer_connection.close()
            
            producer_cursor.close()
            producer_connection.close()
            sys.exit()
        
    def _consume_stream(
        self,
        cursor: ReplicationCursor,
        consumer_connection: Connection,
        consumer_cursor: Cursor
    ) -> None:
        cursor.consume_stream(Callback(TABLE_NAMES, consumer_connection, consumer_cursor))
        
    def _save_start_lsn(self, lsn: int, cursor: Cursor) -> None:
        insert_query = sql.SQL(
            """
             INSERT INTO replication_positions (slot_name, lsn)
             VALUES ({}, {})
             ON CONFLICT (slot_name) DO UPDATE
             SET lsn = excluded.lsn
         """
        )
        cursor.execute(insert_query.format(sql.Literal(REPLICATION_SLOT_NAME), sql.Literal(lsn)))
    
    @staticmethod
    def _get_consumer_connection() -> Connection:
        return psycopg2.connect(consumer_settings.get_connection_string())
    
    @staticmethod
    def _get_consumer_cursor(connection: Connection) -> Cursor:
        return connection.cursor(cursor_factory=Cursor)
        
        
    @staticmethod
    def _create_producer_replication(cursor: ReplicationCursor) -> None:
        try:
            cursor.create_replication_slot(REPLICATION_SLOT_NAME, output_plugin=PLAGIN_NAME)
        except DuplicateObject:
            print(f"Replication slot `{REPLICATION_SLOT_NAME}` already exists, skipping...")
            pass
        
    def _start_producer_replication(self, cursor: ReplicationCursor, start_lsn: int) -> None:
        # Получение последней сохраненной позиции LSN
        cursor.start_replication(slot_name=REPLICATION_SLOT_NAME, decode=True, start_lsn=start_lsn)
    
    @staticmethod
    def _get_start_lsn(consumer_cursor: Cursor) -> int:
        # Получение сохраненной позиции LSN из базы данных
        consumer_cursor.execute(
            sql.SQL("SELECT lsn FROM replication_positions WHERE slot_name = {}")
            .format(sql.Literal(REPLICATION_SLOT_NAME))
        )
        restart_lsn = consumer_cursor.fetchone()
        if restart_lsn:
            return restart_lsn[0]
        else:
            return 0  # Возвращаем начальную позицию LSN для начала чтения с начала WAL журнала
    
    @staticmethod
    def _get_producer_connection() -> LogicalReplicationConnection:
        return psycopg2.connect(
            producer_settings.get_connection_string(),
            connection_factory=LogicalReplicationConnection
        )
    
    @staticmethod
    def _get_producer_cursor(connection: LogicalReplicationConnection) -> ReplicationCursor:
        return connection.cursor(cursor_factory=ReplicationCursor)
    

def run() -> NoReturn:
    print('Initialized consumer...')
    Initializer(TABLE_NAMES).run()
    print("Starting consumer...")
    Customer().start_consume()
    
    
if __name__ == '__main__':
    run()
