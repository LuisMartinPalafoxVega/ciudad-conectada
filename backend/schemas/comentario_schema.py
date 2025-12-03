from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from pydantic import Field

class UsuarioMini(BaseModel):
    id: int
    nombre: str
    email: str
    foto_url: Optional[str] = None    #  👈 AGREGAR ESTO

    class Config:
        from_attributes = True


class ComentarioCreate(BaseModel):
    contenido: str
    parent_id: Optional[int] = None

class ComentarioResponse(BaseModel):
    id: int
    contenido: str
    reporte_id: int
    usuario_id: int
    parent_id: Optional[int] = None
    fecha_creacion: datetime
    usuario: UsuarioMini
    respuestas: List['ComentarioResponse'] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Para que funcione la referencia recursiva
ComentarioResponse.model_rebuild()