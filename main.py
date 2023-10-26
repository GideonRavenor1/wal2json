import json

import psycopg2
from psycopg2 import sql
from psycopg2._psycopg import ReplicationMessage
from psycopg2.extras import LogicalReplicationConnection, ReplicationCursor
from psycopg2.errors import DuplicateObject

replication_slot_name = 'wal2json_slot'
plugin_name = 'wal2json'
TABLES = ('test', 'test_2', 'test_3')


def save_start_lsn(lsn: int):
    # Сохранение позиции LSN в таблицу replication_positions
    with psycopg2.connect(
        dbname="wal2json",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    ) as connection:
        with connection.cursor() as cursor:
            insert_query = sql.SQL(
                """
                 INSERT INTO replication_positions (slot_name, lsn)
                 VALUES ({}, {})
                 ON CONFLICT (slot_name) DO UPDATE
                 SET lsn = excluded.lsn
             """
            )
            cursor.execute(insert_query.format(sql.Literal(replication_slot_name), sql.Literal(lsn)))
            connection.commit()


def get_start_lsn(cursor) -> int:
    # Получение сохраненной позиции LSN из базы данных
    cursor.execute(
        sql.SQL("SELECT lsn FROM replication_positions WHERE slot_name = {}")
        .format(sql.Literal(replication_slot_name))
    )
    restart_lsn = cursor.fetchone()
    if restart_lsn:
        return restart_lsn[0]
    else:
        return 0  # Возвращаем начальную позицию LSN для начала чтения с начала WAL журнала


def callback(message: ReplicationMessage):
    changes = json.loads(message.payload)['change']
    if not changes:
        return
    print('********** Received message **********')
    for change in changes:
        table = change.get('table')
        if table not in TABLES:
            continue
        
        print('All data: ', change)
        print('Send time: ', message.send_time)
        print('Table name: ', table)
        print('Operation: ', change.get('kind'))
        print('Column names: ', change.get('columnnames'))
        print('Column values: ', change.get('columnvalues'))
        print('Old keys: ', change.get('oldkeys'))
        print()
    print('***************************************')


def get_changes():
    connection = psycopg2.connect(
        dbname="wal2json",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432",
        connection_factory=LogicalReplicationConnection
    )
    cursor = connection.cursor(cursor_factory=ReplicationCursor)
    try:
        cursor.create_replication_slot(replication_slot_name, output_plugin=plugin_name)
    except DuplicateObject:
        print(f"Replication slot `{replication_slot_name}` already exists, skipping...")
        pass
        
    # Получение последней сохраненной позиции LSN
    start_lsn = get_start_lsn(cursor)
    cursor.start_replication(slot_name=replication_slot_name, decode=True, start_lsn=start_lsn)
    try:
        print(f"Starting replication stream at LSN `{start_lsn}`")
        cursor.consume_stream(callback)
    except KeyboardInterrupt:
        print("Stopping replication stream...")
    finally:
        # Сохраняем текущую позицию LSN после остановки чтения
        lsn = cursor.wal_end
        print(f"Saving current LSN `{lsn}`")
        save_start_lsn(lsn)
        cursor.close()
        connection.close()
    
    
if __name__ == '__main__':
    get_changes()
