from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select, update, delete
from config.db import Session, meta
from models.user import users
from schemas.user import UserCreate, UserUpdate, UserResponse
from cryptography.fernet import Fernet
from starlette.status import HTTP_204_NO_CONTENT

key = Fernet.generate_key()
f = Fernet(key)

user = APIRouter()


@user.get("/users", response_model=list[UserResponse])
def get_users():
    with Session() as session:
        result = session.execute(select(users)).mappings().all()
        return [dict(row) for row in result]


@user.get("/users/{id}", response_model=UserResponse)
def get_user(id: int):
    with Session() as session:
        result = session.execute(select(users).where(
            users.c.id == id)).mappings().first()
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(result)


@user.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    new_user = {"name": user.name, "email": user.email}
    new_user["password"] = f.encrypt(user.password.encode("utf-8"))

    with Session() as session:
        result = session.execute(users.insert().values(new_user))
        session.commit()  # Confirmar la transacción
        created_user_id = result.inserted_primary_key[0]
        created_user = session.execute(select(users).where(
            users.c.id == created_user_id)).mappings().first()

        if created_user:
            created_user_dict = dict(created_user)
        else:
            created_user_dict = {}

        return created_user_dict


@user.put("/users/{id}", response_model=UserResponse)
def update_user(id: int, user: UserUpdate):
    with Session() as session:
        # Verificar si el usuario existe
        existing_user = session.execute(
            select(users).where(users.c.id == id)).mappings().first()
        if existing_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Preparar los datos para la actualización
        updated_user = {"name": user.name, "email": user.email}
        if user.password:
            updated_user["password"] = f.encrypt(user.password.encode("utf-8"))

        # Ejecutar la actualización
        session.execute(update(users).where(
            users.c.id == id).values(updated_user))
        session.commit()  # Confirmar la transacción

        # Devolver el usuario actualizado
        updated_user = session.execute(
            select(users).where(users.c.id == id)).mappings().first()
        return dict(updated_user)


@user.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int):
    with Session() as session:
        # Verificar si el usuario existe
        user_to_delete = session.execute(select(users).where(
            users.c.id == user_id)).mappings().first()
        if user_to_delete is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Borrar el usuario
        session.execute(delete(users).where(users.c.id == user_id))
        session.commit()  # Confirmar la transacción

        return Response(status_code=HTTP_204_NO_CONTENT)
