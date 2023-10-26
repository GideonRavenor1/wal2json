from abc import ABC, abstractmethod

from psycopg2 import sql
from psycopg2.extensions import cursor as Cursor


class BaseRepository(ABC):
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        raise NotImplementedError
    
    def update(self, cursor: Cursor, id_: int, column_name: str, column_value: str | int, **kwargs) -> None:
        query = sql.SQL(
            """
            UPDATE {table_name} SET {colunm_name} = {column_value} WHERE id = {id_}
            """
        ).format(
            table_name=sql.Identifier(self.table_name),
            id_=sql.Literal(id_),
            column_value=sql.Literal(column_value),
            colunm_name=sql.Identifier(column_name)
        )
        
        cursor.execute(query)
    
    def insert(self, cursor: Cursor, id_: int, column_name: str, column_value: str | int, **kwargs) -> None:
        query = sql.SQL(
            """
            INSERT INTO {table_name} (id, {colunm_name}) VALUES ({id_},{column_value})
            """
        ).format(
            table_name=sql.Identifier(self.table_name),
            colunm_name=sql.Identifier(column_name),
            column_value=sql.Literal(column_value),
            id_=sql.Literal(id_)
        )
        
        cursor.execute(query)
    
    def delete(self, cursor: Cursor, deleted_id: int, **kwargs) -> None:
        query = sql.SQL(
            """
            DELETE FROM {table_name} WHERE id = {id_}
            """
        ).format(
            table_name=sql.Identifier(self.table_name),
            id_=sql.Literal(deleted_id),
        )
        
        cursor.execute(query)
