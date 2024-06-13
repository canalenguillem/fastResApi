from sqlalchemy import Table, Column, Integer, String, MetaData
from config.db import meta, engine

role = Table(
    'role', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(50), unique=True)
)

meta.create_all(engine)
