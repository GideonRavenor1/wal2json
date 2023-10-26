from psycopg2 import sql
from psycopg2.extras import DictCursor

COLUMN_TYPES_MAP = {
    'character varying': 'TEXT',
    'integer': 'INT',
    # Можно дополнить своими типами,
    # так же придумать варианты как проставить доп.настройки, например когда задан типа VARCHAR с ограничением на длину
    # символов
}


class DDLExtractor:
    
    def __init__(self, cursor: DictCursor, table_name: str) -> None:
        self.cursor = cursor
        self.table_name = table_name
        
    def extract(self) -> str:
        query = self.select_information_schema_query
        self.cursor.execute(query)
        
        ddl_columns_parameters_strings = []
        for row in self.cursor.fetchall():
            column_name = row['column_name']
            column_type = COLUMN_TYPES_MAP.get(row['data_type'])
            ddl_string = f'{column_name} {column_type}'
            ddl_columns_parameters_strings.append(ddl_string)
        return self.build_ddl_query(ddl_columns_parameters_strings)
    
    @property
    def select_information_schema_query(self) -> str:
        return sql.SQL(
            """
            SELECT column_name, data_type
            FROM information_schema.columns WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            AND table_name = {table_name} ORDER BY table_schema, table_name
            """
        ).format(table_name=sql.Literal(self.table_name))
    
    def build_ddl_query(self, ddl_columns_parameters_strings: list[str]) -> str:
        return (
            """
            CREATE TABLE IF NOT EXISTS {table_name} (
                {ddl_columns_parameters_strings}
            )
            """
        ).format(
            table_name=self.table_name,
            ddl_columns_parameters_strings=', '.join(ddl_columns_parameters_strings)
        )
