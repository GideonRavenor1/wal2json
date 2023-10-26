from random import choice

from producer.base_repository import BaseRepository

DATA = [
    111,
    222,
    333,
    444,
    555
]


class RepositoryTestThree(BaseRepository):
    table_name = 'test_3'
    main_column_name = 'number'
    
    def get_random_element(self) -> int:
        return choice(DATA)
