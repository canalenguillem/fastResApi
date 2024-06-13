from pydantic import BaseModel
from typing import Optional
from schemas.role import RoleResponse


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str
    role_id: int  # Agregar el role_id aquí


class UserUpdate(UserBase):
    password: Optional[str] = None
    role_id: Optional[int] = None  # Agregar el role_id aquí


class UserResponse(UserBase):
    id: int
    role: RoleResponse  # Incluir el rol en la respuesta

    class Config:
        from_attributes = True  # Actualización para Pydantic v2
