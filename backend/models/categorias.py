from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    icono = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)

    reportes = relationship("Reporte", back_populates="categoria")