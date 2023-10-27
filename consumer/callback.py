import json

from psycopg2._psycopg import ReplicationMessage
from psycopg2.extensions import connection as Connection, cursor as Cursor

from consumer.base_repository import BaseRepository
from consumer.repository_test_one import RepositoryTestOne
from consumer.repository_test_three import RepositoryTestThree
from consumer.repository_test_two import RepositoryTestTwo

REPOSORORIES = {
    'test_1': RepositoryTestOne,
    'test_2': RepositoryTestTwo,
    'test_3': RepositoryTestThree
}


class Callback:
    def __init__(self, table_names: list[str], consumer_connection: Connection, consumer_cursor: Cursor) -> None:
        self.table_names = table_names
        self.consumer_connection = consumer_connection
        self.consumer_cursor = consumer_cursor
    
    def __call__(self, message: ReplicationMessage) -> None:
        changes = json.loads(message.payload)['change']
        if not changes:
            return
        print('********** Received message **********')
        for change in changes:
            table = change.get('table')
            if table not in self.table_names:
                continue
            
            operation = change.get('kind')
            column_names = change.get('columnnames')
            column_values = change.get('columnvalues')
            old_keys = change.get('oldkeys')
            
            print('All data: ', change)
            print('Table name: ', table)
            print('Operation: ', operation)
            print('Column names: ', column_names)
            print('Column values: ', column_values)
            print('Old keys: ', old_keys)
            print()
            
            params = {
                'id_': column_values[0] if column_names else None,
                'column_name': column_names[1] if column_names else None,
                'column_value': column_values[1] if column_names else None,
                'deleted_id': old_keys['keyvalues'][0] if old_keys else None
            }
            repository = self._get_repository_by_table_name(table)()
            self._execute_command(repository, operation, **params)
            self.consumer_connection.commit()
        print('***************************************')
        
    def _get_repository_by_table_name(self, table_name: str) -> type[BaseRepository]:
        return REPOSORORIES[table_name]
    
    def _execute_command(self, repository: BaseRepository, method: str, **kwargs) -> None:
        getattr(repository, method)(cursor=self.consumer_cursor, **kwargs)
