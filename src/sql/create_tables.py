import sqlalchemy
from sqlalchemy.engine import create_engine
from sqlalchemy import TextClause
import os
import sys
import pathlib


with open("azure_pg_database_connection.key", "r") as file:
    conn_string = file.read()
    conn_string = "postgresql+psycopg2" + conn_string


engine = create_engine(conn_string)

with engine.connect() as conn:
    
    for sql_file_path in pathlib.Path("sql").iterdir():
        
        with open(sql_file_path.absolute(), "r") as file:
            sql_script = TextClause(file.read())
            conn.execute(sql_script)
            conn.commit()