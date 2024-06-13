from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select, delete, insert
from sqlalchemy.orm import sessionmaker
from starlette.status import HTTP_204_NO_CONTENT
from config.db import engine
from models.role import role
from models.user import user
from schemas.role import RoleResponse, RoleCreate

Session = sessionmaker(bind=engine)
role_router = APIRouter()


@role_router.get("/roles", response_model=list[RoleResponse], tags=["Roles"])
def get_roles():
    with Session() as session:
        result = session.execute(select(role)).fetchall()
        return [RoleResponse.from_orm(row) for row in result]


@role_router.post("/roles", response_model=RoleResponse, tags=["Roles"])
def create_role(role_data: RoleCreate):
    new_role = {"name": role_data.name}
    with Session() as session:
        result = session.execute(insert(role).values(new_role))
        session.commit()
        created_role = session.execute(select(role).where(
            role.c.id == result.inserted_primary_key[0])).first()
        return RoleResponse.from_orm(created_role)


@role_router.delete("/roles/{role_id}", tags=["Roles"])
def delete_role(role_id: int):
    with Session() as session:
        # Verificar si el rol está asignado a algún usuario
        assigned_users = session.execute(
            select(user).where(user.c.role_id == role_id)).fetchall()
        if assigned_users:
            raise HTTPException(
                status_code=400, detail="Role is assigned to one or more users and cannot be deleted.")

        # Eliminar el rol
        session.execute(delete(role).where(role.c.id == role_id))
        session.commit()

        return Response(status_code=HTTP_204_NO_CONTENT)
