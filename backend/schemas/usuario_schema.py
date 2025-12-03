from pydantic import BaseModel, EmailStr
from datetime import datetime
from schemas.comentario_schema import ComentarioResponse
from sqlalchemy.orm import relationship
from typing import List


class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    email: EmailStr | None = None

    class Config:
        from_attributes = True


class CambiarPassword(BaseModel):
    password_actual: str
    password_nueva: str


class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        from_attributes = True


class UsuarioDetalle(UsuarioResponse):
    fecha_registro: datetime
    activo: bool
    comentarios: List[ComentarioResponse] = []

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None

class CambiarPassword(BaseModel):
    password_actual: str
    password_nueva: str

class UsuarioDetalle(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    fecha_registro: datetime
    activo: bool
    foto_url: Optional[str] = None  # ✅ AGREGAR ESTE CAMPO
    total_reportes: int = 0
    reportes_pendientes: int = 0
    reportes_resueltos: int = 0

    class Config:
        from_attributes = True