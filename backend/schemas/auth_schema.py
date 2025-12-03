from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UsuarioInfo(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool
    fecha_registro: datetime
    foto_url: Optional[str] = None  # ✅ AGREGAR ESTE CAMPO

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    usuario: UsuarioInfo