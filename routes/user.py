from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select, update, delete
from config.db import Session, meta
from models.user import user
from models.role import role  # Importar el modelo de rol
from schemas.user import UserCreate, UserUpdate, UserResponse
from cryptography.fernet import Fernet
from starlette.status import HTTP_204_NO_CONTENT

key = Fernet.generate_key()
f = Fernet(key)

user_router = APIRouter()


@user_router.get("/users", response_model=list[UserResponse], tags=["Users"])
def get_users():
    with Session() as session:
        result = session.execute(
            select(user.c.id, user.c.name, user.c.email, role.c.id.label(
                'role_id'), role.c.name.label('role_name'))
            .select_from(user.join(role, user.c.role_id == role.c.id))
        ).all()
        return [
            {"id": row.id, "name": row.name, "email": row.email,
                "role": {"id": row.role_id, "name": row.role_name}}
            for row in result
        ]


@user_router.get("/users/{id}", response_model=UserResponse, tags=["Users"])
def get_user(id: int):
    with Session() as session:
        result = session.execute(
            select(user.c.id, user.c.name, user.c.email, role.c.id.label(
                'role_id'), role.c.name.label('role_name'))
            .select_from(user.join(role, user.c.role_id == role.c.id))
            .where(user.c.id == id)
        ).first()
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": result.id, "name": result.name, "email": result.email, "role": {"id": result.role_id, "name": result.role_name}}


@user_router.post("/users", response_model=UserResponse, tags=["Users"])
def create_user(user: UserCreate):
    new_user = {"name": user.name, "email": user.email}
    new_user["password"] = f.encrypt(user.password.encode("utf-8"))
    new_user["role_id"] = user.role_id

    with Session() as session:
        result = session.execute(user.insert().values(new_user))
        session.commit()  # Confirmar la transacción
        created_user_id = result.inserted_primary_key[0]
        created_user = session.execute(
            select(user.c.id, user.c.name, user.c.email, role.c.id.label(
                'role_id'), role.c.name.label('role_name'))
            .select_from(user.join(role, user.c.role_id == role.c.id))
            .where(user.c.id == created_user_id)
        ).first()

        if created_user:
            created_user_dict = {"id": created_user.id, "name": created_user.name, "email": created_user.email, "role": {
                "id": created_user.role_id, "name": created_user.role_name}}
        else:
            created_user_dict = {}

        return created_user_dict


@user_router.put("/users/{id}", response_model=UserResponse, tags=["Users"])
def update_user(id: int, user: UserUpdate):
    with Session() as session:
        # Verificar si el usuario existe
        existing_user = session.execute(
            select(user).where(user.c.id == id)).first()
        if existing_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Preparar los datos para la actualización
        updated_user = {"name": user.name, "email": user.email}
        if user.password:
            updated_user["password"] = f.encrypt(user.password.encode("utf-8"))
        if user.role_id:
            updated_user["role_id"] = user.role_id

        # Ejecutar la actualización
        session.execute(update(user).where(
            user.c.id == id).values(updated_user))
        session.commit()  # Confirmar la transacción

        # Devolver el usuario actualizado
        updated_user = session.execute(
            select(user.c.id, user.c.name, user.c.email, role.c.id.label(
                'role_id'), role.c.name.label('role_name'))
            .select_from(user.join(role, user.c.role_id == role.c.id))
            .where(user.c.id == id)
        ).first()
        return {"id": updated_user.id, "name": updated_user.name, "email": updated_user.email, "role": {"id": updated_user.role_id, "name": updated_user.role_name}}


@user_router.delete("/users/{user_id}", response_model=dict, tags=["Users"])
def delete_user(user_id: int):
    with Session() as session:
        # Verificar si el usuario existe
        user_to_delete = session.execute(
            select(user).where(user.c.id == user_id)).first()
        if user_to_delete is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Borrar el usuario
        session.execute(delete(user).where(user.c.id == user_id))
        session.commit()  # Confirmar la transacción

        return Response(status_code=HTTP_204_NO_CONTENT)
