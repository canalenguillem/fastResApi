from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "mysql+pymysql://guillem:guillem@localhost:3306/storedb")
meta = MetaData()
Session = sessionmaker(bind=engine)
conn = engine.connect()
