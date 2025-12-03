from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class HistorialEstado(Base):
    __tablename__ = "historial_estados"

    id = Column(Integer, primary_key=True, index=True)
    reporte_id = Column(Integer, ForeignKey("reportes.id", ondelete="CASCADE"), nullable=False)
    estado_anterior = Column(String(20), nullable=True)
    estado_nuevo = Column(String(20), nullable=False)
    admin_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    comentario = Column(Text, nullable=True)
    fecha_cambio = Column(DateTime(timezone=True), server_default=func.now())

    reporte = relationship("Reporte", back_populates="historial")