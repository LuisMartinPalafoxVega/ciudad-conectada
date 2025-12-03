from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class RolEnum(str, enum.Enum):
    ciudadano = "ciudadano"
    administrador = "administrador"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(SQLEnum(RolEnum), default=RolEnum.ciudadano, nullable=False)
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, server_default=func.now())
    foto_url = Column(String(255), nullable=True)  # ✅ ASEGÚRATE DE QUE EXISTA

    # Relaciones
    reportes = relationship("Reporte", back_populates="usuario")
    comentarios = relationship("Comentario", back_populates="usuario")
    likes = relationship("LikeReporte", back_populates="usuario")