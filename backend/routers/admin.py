from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from models.reportes import Reporte
from models.usuarios import Usuario
from dependencies import get_current_admin
from sqlalchemy.orm import joinedload
from fastapi import status

router = APIRouter(
    tags=["Admin"]
)


@router.delete("/reportes/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_reporte(
        id: int,
        db: Session = Depends(get_db),
        admin: Usuario = Depends(get_current_admin)
):
    reporte = db.query(Reporte).filter(Reporte.id == id).first()
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    db.delete(reporte)
    db.commit()   # 👈 aquí aplicas el borrado real
    return {"message": "Reporte eliminado"}



@router.put("/reportes/{id}/estado")
def actualizar_estado_reporte(
    id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    reporte = db.query(Reporte).filter(Reporte.id == id).first()
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    nuevo_estado = data.get("estado")
    comentario = data.get("comentario")

    if nuevo_estado:
        reporte.estado = nuevo_estado

    if comentario:
        reporte.comentario_admin = comentario

    db.commit()
    db.refresh(reporte)

    return {"message": "Estado actualizado", "reporte": reporte}


@router.get("/reportes/{id}/historial")
def obtener_historial_reporte(id: int, db: Session = Depends(get_db)):
    historial = (
        db.query(Reporte)
        .filter(Reporte.id == id)
        .first()
    )

    if not historial:
        raise HTTPException(status_code=404, detail="Historial no encontrado")

    return historial


@router.get("/estadisticas")
def get_estadisticas(db: Session = Depends(get_db)):
    total = db.query(Reporte).count()
    pendientes = db.query(Reporte).filter(Reporte.estado == "pendiente").count()
    en_proceso = db.query(Reporte).filter(Reporte.estado == "en_proceso").count()
    resueltos = db.query(Reporte).filter(Reporte.estado == "resuelto").count()

    porcentaje_resueltos = round((resueltos / total) * 100) if total > 0 else 0

    return {
        "total_reportes": total,
        "pendientes": pendientes,
        "en_proceso": en_proceso,
        "resueltos": resueltos
    }


from sqlalchemy import desc, func


@router.get("/reportes")
def admin_listar_reportes(
    estado: str = None,
    orden: str = None,  # 👈 nuevo parámetro
    page: int = 1,
    per_page: int = 1000,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_admin)
):
    query = db.query(Reporte).options(
        joinedload(Reporte.categoria),
        joinedload(Reporte.usuario),
        joinedload(Reporte.likes)
    )

    if estado:
        query = query.filter(Reporte.estado == estado)

    # 👇 ordenamiento dinámico
    if orden == "likes":
        query = query.outerjoin(Reporte.likes).group_by(Reporte.id).order_by(desc(func.count(Reporte.likes)))
    elif orden == "fecha":
        query = query.order_by(desc(Reporte.fecha_creacion))

    total = query.count()
    reportes = query.offset((page - 1) * per_page).limit(per_page).all()

    # serialización como ya lo tienes
    items = [{
        "id": r.id,
        "titulo": r.titulo,
        "descripcion": r.descripcion,
        "estado": r.estado.value if hasattr(r.estado, "value") else r.estado,
        "fecha_creacion": r.fecha_creacion.isoformat(),
        "usuario": {
            "id": r.usuario.id,
            "nombre": r.usuario.nombre,
            "email": r.usuario.email
        } if r.usuario else None,
        "categoria": {
            "id": r.categoria.id,
            "nombre": r.categoria.nombre,
            "color": r.categoria.color,
            "icono": r.categoria.icono
        } if r.categoria else None,
        "total_likes": r.total_likes
    } for r in reportes]

    return {
        "total": total,
        "items": items,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
        "has_next": page * per_page < total,
        "has_prev": page > 1
    }




