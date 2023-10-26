from abc import ABC, abstractmethod

from psycopg2 import sql
from psycopg2.extensions import cursor as Cursor


class BaseRepository(ABC):
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def main_column_name(self) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def get_random_element(self) -> str | int:
        raise NotImplementedError
    
    def update(self, cursor: Cursor) -> None:
        element = self.get_random_element()
        print("Chosen element: ", element)
        new_element = self.get_random_element()
        print("Chosen new element: ", element)
        
        query = sql.SQL(
            """
            UPDATE {table_name} SET {colunm_name} = {new_element} WHERE {colunm_name} = {element}
            """
        ).format(
            table_name=sql.Identifier(self.table_name),
            new_element=sql.Literal(new_element),
            element=sql.Literal(element),
            colunm_name=sql.Identifier(self.main_column_name)
        )
        
        cursor.execute(query)
    
    def insert(self, cursor: Cursor) -> None:
        element = self.get_random_element()
        print("Chosen element: ", element)
        
        query = sql.SQL(
            """
            INSERT INTO {table_name} ({colunm_name}) VALUES ({element})
            """
        ).format(
            table_name=sql.Identifier(self.table_name),
            element=sql.Literal(element),
            colunm_name=sql.Identifier(self.main_column_name)
        )
        
        cursor.execute(query)
    
    def delete(self, cursor: Cursor) -> None:
        element = self.get_random_element()
        print("Chosen element: ", element)
        
        query = sql.SQL(
            """
            DELETE FROM {table_name} WHERE {colunm_name} = {element}
            """
        ).format(
            table_name=sql.Identifier(self.table_name),
            element=sql.Literal(element),
            colunm_name=sql.Identifier(self.main_column_name)
        )
        
        cursor.execute(query)
