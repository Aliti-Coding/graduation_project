from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Sequence
from sqlalchemy.orm import declarative_base, Session


with open("sql_password.key", "r") as f:
    password_key = f.read()
    

USERNAME = "postgres"
PASSWORD = password_key
PORT = 5432
DATABASE = "postgres"
HOST = "localhost"

engine = create_engine(f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

Base = declarative_base()

session = Session(bind=engine) # starting a session to interact with the database

class TrustPilotDB(Base):
    __tablename__ = "trust_pilot"
    id = Column(Integer, primary_key=True) #auto increment is true by default
    text = Column(String)
    rating = Column(Integer)
    title = Column(String)
    date = Column(DateTime)
    
    def __repr__(self):
        return f"< text={self.text} rating={self.rating} title={self.title} date={self.date}"

class NewsApiDB(Base):
    __tablename__ = "news_api"
    id = Column(Integer, primary_key=True)
    source = Column(String)
    author = Column(String)
    title = Column(String)
    description = Column(String)
    url = Column(String)
    publishedAt = Column(String)
    content = Column(String)

    def __repr__(self):
        return f"< source={self.source} author={self.author} title={self.title} description={self.description} url={self.url} publishedAt={self.publishedAt} content={self.content}"
    

#syntax for creating all tables written as classes
# Base.metadata.create_all(engine)



#inserting rows to table example
# start a session
#insert_row = TrustPilotDB(text="Was a horrible experience", rating=2, title="Horrible", date="1998-09-20")
# session.add(insert_row)
# session.commit()


