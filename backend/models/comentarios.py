from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    contenido = Column(Text, nullable=False)
    reporte_id = Column(Integer, ForeignKey("reportes.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comentarios.id", ondelete="CASCADE"), nullable=True)
    fecha_creacion = Column(
        DateTime,
        default=func.now(),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones externas
    reporte = relationship("Reporte", back_populates="comentarios")
    usuario = relationship("Usuario", back_populates="comentarios")

    # Relación con comentario padre
    parent = relationship(
        "Comentario",
        remote_side=[id],
        back_populates="respuestas"
    )

    # Respuestas
    respuestas = relationship(
        "Comentario",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
