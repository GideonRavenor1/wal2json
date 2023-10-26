from random import choice

from producer.base_repository import BaseRepository

DATA = [
    'John',
    'Mark',
    'Victor',
    'Anna',
    'Olga',
]


class RepositoryTestOne(BaseRepository):
    table_name = 'test_1'
    main_column_name = 'name'
    
    def get_random_element(self) -> str:
        return choice(DATA)
