from sqlalchemy.engine import create_engine
from sqlalchemy import TextClause
import pathlib

# Get and create postgressql connection string
with open("azure_pg_database_connection.key", "r") as file:
    conn_string = file.read()
    conn_string = "postgresql+psycopg2" + conn_string


engine = create_engine(conn_string)


# Connect to database
with engine.connect() as conn:

    # Iterate over paths to sql-table scripts 
    for sql_file_path in pathlib.Path("sql").iterdir():
        
        # Read content of scripts
        with open(sql_file_path.absolute(), "r") as file:
            sql_script = TextClause(file.read())
            
            # Execute script and create tables in database
            conn.execute(sql_script)
            conn.commit()