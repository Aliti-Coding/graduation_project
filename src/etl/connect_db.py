from sqlalchemy import create_engine, Engine

def connect_to_grad_db() -> Engine:
    """
    Connects to grad project db.

    ## Returns:
    sqlalchemy.Engine
    """

    # Get and create connection string
    with open("../../azure_pg_database_connection.key", "r") as file:
        conn_string = file.read()
        conn_string = "postgresql+psycopg2" + conn_string

    return create_engine(conn_string)