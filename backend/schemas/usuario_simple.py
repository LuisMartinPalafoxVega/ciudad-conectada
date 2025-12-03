from pydantic import BaseModel
from sqlalchemy.orm import relationship


class UsuarioSimple(BaseModel):
    id: int
    nombre: str
    foto_url: str | None = None

    class Config:
        from_attributes = True

comentarios = relationship("Comentario", back_populates="usuario")
