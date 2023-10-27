import sys
from random import choice
from time import sleep
from typing import NoReturn

import psycopg2
from psycopg2.extensions import cursor as Cursor

from config import producer_settings
from producer.base_repository import BaseRepository
from producer.repository_test_one import RepositoryTestOne
from producer.repository_test_three import RepositoryTestThree
from producer.repository_test_two import RepositoryTestTwo

REPOSORORIES = (RepositoryTestOne, RepositoryTestTwo, RepositoryTestThree)
TABLE_METHODS = ('update', 'insert', 'delete')

SLEEP_TIME = 2

settings = producer_settings


class Producer:
    
    def __init__(self, cursor: Cursor) -> None:
        self.cursor = cursor
    
    def execute_command_in_random_table(self) -> None:
        randon_repository = self._get_random_table()()
        print("Chosen table: ", randon_repository.table_name)
        random_method = self._get_random_table_method()
        print("Chosen method: ", random_method)
        self._execute_command(randon_repository, random_method)
    
    @staticmethod
    def _get_random_table() -> type[BaseRepository]:
        return choice(REPOSORORIES)
    
    @staticmethod
    def _get_random_table_method() -> str:
        return choice(TABLE_METHODS)
    
    def _execute_command(self, repository: BaseRepository, random_method: str) -> None:
        getattr(repository, random_method)(self.cursor)


def run() -> NoReturn:
    print('Starting producer...')
    print("Connecting to database...")
    with psycopg2.connect(settings.get_connection_string()) as connection:
        with connection.cursor() as cursor:
            producer = Producer(cursor)
            try:
                while True:
                    print("*" * 20)
                    producer.execute_command_in_random_table()
                    connection.commit()
                    print()
                    print("*" * 20)
                    
                    sleep(SLEEP_TIME)
            except KeyboardInterrupt:
                print('Stopped producer..')
                sys.exit()


if __name__ == '__main__':
    run()
