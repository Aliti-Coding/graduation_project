from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

# username=
# password = 
# port = 
# database=
# full_url = 
# host = 

engine = create_engine(fr"postgresql://{username}:{password}@{host}:{port}/pgsql-graduate-gruppe4")

# conn = engine.connect()

meta = MetaData()

students = Table(
    'youtube_comments', meta,
    Column('id', Integer, primary_key= True),
    Column('publish_date', String),
    Column('comment_text', String)
)
meta.create_all(engine)

