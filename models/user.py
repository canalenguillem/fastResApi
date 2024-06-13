from sqlalchemy import Table, Column, Integer, String, ForeignKey
from config.db import meta, engine
from models.role import role  # Importar el modelo de rol

user = Table(
    'user', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('email', String(50), unique=True),
    Column('password', String(200)),
    Column('role_id', Integer, ForeignKey('role.id'))
)

meta.create_all(engine)
