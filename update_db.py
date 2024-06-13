from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, select, insert, update, inspect, text
from sqlalchemy.schema import DDL
from sqlalchemy.orm import sessionmaker
from config.db import engine

# Crear una sesión
Session = sessionmaker(bind=engine)
session = Session()

# Conectar a la base de datos y obtener metadatos
metadata = MetaData()

# Definir la tabla role
role = Table(
    'role', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50), unique=True)
)

# Definir la tabla user con la nueva columna role_id
user = Table(
    'user', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('email', String(50), unique=True),
    Column('password', String(200)),
    Column('role_id', Integer, ForeignKey('role.id'))
)

# Crear la tabla role
metadata.create_all(engine, tables=[role])

# Añadir la columna role_id a la tabla user (ya existente)
inspector = inspect(engine)

if not inspector.has_table('user'):
    raise Exception("The user table does not exist.")

# Verificar si la columna role_id ya existe
columns = inspector.get_columns('user')
if not any(col['name'] == 'role_id' for col in columns):
    alter_table = DDL("ALTER TABLE user ADD COLUMN role_id INTEGER")
    session.execute(alter_table)

# Eliminar todos los registros de la tabla role y resetear el auto_increment
print("Cleaning roles table")
session.execute(text("DELETE FROM role"))
session.execute(text("ALTER TABLE role AUTO_INCREMENT = 1"))
session.commit()  # Confirmar la transacción para asegurar que los roles se eliminan y el ID se restablece

# Insertar los roles 'admin' y 'user'
print("Inserting roles 'admin' and 'user'")
session.execute(role.insert().values([
    {"name": "admin"},
    {"name": "user"}
]))
session.commit()  # Confirmar la transacción para asegurar que los roles se insertan

# Verificar que los roles se insertaron correctamente
result = session.execute(select(role.c.id, role.c.name))
roles_inserted = result.fetchall()
print(f"Roles inserted: {roles_inserted}")

# Obtener el ID del rol 'user'
result = session.execute(select(role.c.id).where(role.c.name == 'user'))
user_role_id = result.fetchone()[0]
print(f"User role ID: {user_role_id}")

# Asignar el rol 'user' a todos los usuarios existentes
print("Updating existing users to have role 'user'")
session.execute(update(user).values(role_id=user_role_id))
session.commit()  # Confirmar la transacción para asegurar que los usuarios se actualizan

# Verificar que los usuarios se actualizaron correctamente
result = session.execute(select(user.c.id, user.c.role_id))
users_updated = result.fetchall()
print(f"Users updated: {users_updated}")

print("Database updated successfully!")

# Cerrar la sesión
session.close()
