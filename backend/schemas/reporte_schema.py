from pydantic import BaseModel
from datetime import datetime
from schemas.usuario_schema import UsuarioResponse
from schemas.categoria_schema import CategoriaResponse
from schemas.like_schema import LikeResponse

class ReporteBase(BaseModel):
    titulo: str
    descripcion: str
    categoria_id: int
    latitud: float
    longitud: float
    direccion_referencia: str | None = None
    imagen_url: str | None = None


class ReporteCreate(ReporteBase):
    usuario_id: int


class ReporteUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    categoria_id: int | None = None
    latitud: float | None = None
    longitud: float | None = None
    direccion_referencia: str | None = None
    imagen_url: str | None = None
    estado: str | None = None


class ReporteResponse(ReporteBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime | None = None
    estado: str
    urgencia: str = "media"
    score_urgencia: float = 0.0
    usuario_id: int
    usuario: UsuarioResponse
    categoria: CategoriaResponse
    total_likes: int = 0
    usuario_dio_like: bool = False

    class Config:
        from_attributes = True


class ReportesPaginados(BaseModel):
    items: list[ReporteResponse]
    page: int
    pages: int
    has_next: bool
    has_prev: bool