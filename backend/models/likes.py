from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

import enum

class LikeReporte(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    reporte_id = Column(Integer, ForeignKey("reportes.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    fecha_like = Column(DateTime(timezone=True), server_default=func.now())

    reporte = relationship("Reporte", back_populates="likes")
    usuario = relationship("Usuario", back_populates="likes")

