from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from models.reportes import Reporte, EstadoEnum
from models.categorias import Categoria
from dependencies import get_current_user

router = APIRouter(tags=["Mapa"])


@router.get("/heatmap")
def obtener_datos_heatmap(
    categoria_id: Optional[int] = None,
    estado: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtener datos para el mapa de calor"""
    
    query = db.query(
        Reporte.id,
        Reporte.latitud,
        Reporte.longitud,
        Reporte.titulo,
        Reporte.estado,
        Reporte.fecha_creacion,
        Categoria.nombre.label('categoria_nombre'),
        Categoria.color.label('categoria_color'),
        Categoria.icono.label('categoria_icono')
    ).join(Categoria)
    
    # Filtros
    if categoria_id:
        query = query.filter(Reporte.categoria_id == categoria_id)
    
    if estado:
        query = query.filter(Reporte.estado == estado)
    
    if fecha_inicio:
        query = query.filter(Reporte.fecha_creacion >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(Reporte.fecha_creacion <= fecha_fin)
    
    reportes = query.all()
    
    # Formatear datos para el mapa de calor
    heatmap_data = []
    markers_data = []
    
    for r in reportes:
        # Datos para heatmap (solo coordenadas + intensidad)
        heatmap_data.append({
            "lat": float(r.latitud),
            "lng": float(r.longitud),
            "intensity": 1  # Puedes ajustar según importancia
        })
        
        # Datos para marcadores (info completa)
        markers_data.append({
            "id": r.id,
            "lat": float(r.latitud),
            "lng": float(r.longitud),
            "titulo": r.titulo,
            "estado": r.estado.value,
            "categoria": r.categoria_nombre,
            "categoria_color": r.categoria_color,
            "categoria_icono": r.categoria_icono,
            "fecha": r.fecha_creacion.isoformat()
        })
    
    return {
        "heatmap": heatmap_data,
        "markers": markers_data,
        "total": len(reportes)
    }


@router.get("/estadisticas-zona")
def obtener_estadisticas_zona(
    lat_min: float,
    lat_max: float,
    lng_min: float,
    lng_max: float,
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de una zona específica"""
    
    reportes = db.query(Reporte).filter(
        and_(
            Reporte.latitud >= lat_min,
            Reporte.latitud <= lat_max,
            Reporte.longitud >= lng_min,
            Reporte.longitud <= lng_max
        )
    ).all()
    
    # Estadísticas
    total = len(reportes)
    pendientes = sum(1 for r in reportes if r.estado == EstadoEnum.pendiente)
    en_proceso = sum(1 for r in reportes if r.estado == EstadoEnum.en_proceso)
    resueltos = sum(1 for r in reportes if r.estado == EstadoEnum.resuelto)
    
    # Por categoría
    categorias = db.query(
        Categoria.nombre,
        Categoria.color,
        func.count(Reporte.id).label('total')
    ).join(Reporte).filter(
        and_(
            Reporte.latitud >= lat_min,
            Reporte.latitud <= lat_max,
            Reporte.longitud >= lng_min,
            Reporte.longitud <= lng_max
        )
    ).group_by(Categoria.id).all()
    
    return {
        "total": total,
        "pendientes": pendientes,
        "en_proceso": en_proceso,
        "resueltos": resueltos,
        "por_categoria": [
            {
                "nombre": c.nombre,
                "color": c.color,
                "total": c.total
            }
            for c in categorias
        ]
    }


@router.get("/timeline")
def obtener_timeline(
    dias: int = 30,
    db: Session = Depends(get_db)
):
    """Obtener timeline de reportes"""
    
    fecha_inicio = datetime.now() - timedelta(days=dias)
    
    timeline = db.query(
        func.date(Reporte.fecha_creacion).label('fecha'),
        func.count(Reporte.id).label('total')
    ).filter(
        Reporte.fecha_creacion >= fecha_inicio
    ).group_by(
        func.date(Reporte.fecha_creacion)
    ).order_by('fecha').all()
    
    return {
        "timeline": [
            {
                "fecha": t.fecha.isoformat(),
                "total": t.total
            }
            for t in timeline
        ]
    }


@router.get("/zonas-criticas")
def obtener_zonas_criticas(
    limite: int = 5,
    db: Session = Depends(get_db)
):
    """Identificar las zonas con más problemas"""
    
    # Dividir el mapa en cuadrículas y contar reportes
    # Esto es una simplificación - en producción usarías un algoritmo más sofisticado
    
    reportes = db.query(
        Reporte.latitud,
        Reporte.longitud,
        Reporte.estado
    ).all()
    
    # Agrupar por coordenadas aproximadas (redondear a 3 decimales)
    from collections import defaultdict
    zonas = defaultdict(lambda: {"total": 0, "pendientes": 0, "lat": 0, "lng": 0})
    
    for r in reportes:
        lat_round = round(r.latitud, 3)
        lng_round = round(r.longitud, 3)
        key = f"{lat_round},{lng_round}"
        
        zonas[key]["total"] += 1
        zonas[key]["lat"] = lat_round
        zonas[key]["lng"] = lng_round
        
        if r.estado == EstadoEnum.pendiente:
            zonas[key]["pendientes"] += 1
    
    # Ordenar por total y tomar las top N
    zonas_criticas = sorted(
        zonas.values(),
        key=lambda x: x["total"],
        reverse=True
    )[:limite]
    
    return {
        "zonas_criticas": zonas_criticas
    }