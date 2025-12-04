from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class EstadoEnum(str, enum.Enum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    resuelto = "resuelto"

class UrgenciaEnum(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"
    critica = "critica"

class Reporte(Base):
    __tablename__ = "reportes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False)

    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    direccion_referencia = Column(String(300), nullable=True)
    imagen_url = Column(String(500), nullable=True)
    estado = Column(Enum(EstadoEnum), default=EstadoEnum.pendiente)
    urgencia = Column(Enum(UrgenciaEnum), default=UrgenciaEnum.media)
    score_urgencia = Column(Float, default=0.0)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # relaciones
    usuario = relationship("Usuario", back_populates="reportes", passive_deletes=True)
    categoria = relationship("Categoria", back_populates="reportes", passive_deletes=True)
    likes = relationship("LikeReporte", back_populates="reporte", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="reporte", cascade="all, delete-orphan")

    @property
    def total_likes(self):
        return len(self.likes)
