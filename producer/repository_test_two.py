from random import choice

from producer.base_repository import BaseRepository

DATA = [
    'example@example.com',
    'test@example.com',
    'psql@localhost.com',
    'email@gmail.com',
    'kafka@localhost.com',
]


class RepositoryTestTwo(BaseRepository):
    table_name = 'test_2'
    main_column_name = 'email'
    
    def get_random_element(self) -> str:
        return choice(DATA)
