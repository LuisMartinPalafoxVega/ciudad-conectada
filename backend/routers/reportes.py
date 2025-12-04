from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from models.usuarios import Usuario
from models.reportes import Reporte
from models.categorias import Categoria
from models.likes import LikeReporte
from models.comentarios import Comentario
from dependencies import get_current_user
from schemas.comentario_schema import ComentarioResponse
from schemas.reporte_schema import ReporteResponse, ReportesPaginados
from services.urgencia_service import calcular_score_urgencia, actualizar_urgencia_reporte
import shutil
import os

router = APIRouter(tags=["Reportes"])


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



# ============================================
# 📋 MIS REPORTES
# ============================================
@router.get("/mis-reportes/todos", response_model=ReportesPaginados)
def obtener_mis_reportes(
        page: int = 1,
        per_page: int = 12,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)  # ← AQUÍ
):
    usuario_id = current_user.id

    query = db.query(Reporte).filter(Reporte.usuario_id == usuario_id)

    total = query.count()
    pages = max(1, (total + per_page - 1) // per_page)

    reportes = (
        query
        .order_by(Reporte.fecha_creacion.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    reportes_con_likes = []
    for reporte in reportes:
        total_likes = db.query(func.count(LikeReporte.id)).filter(
            LikeReporte.reporte_id == reporte.id
        ).scalar() or 0

        # ← VERIFICAR SI EL USUARIO DIO LIKE
        usuario_dio_like = db.query(LikeReporte).filter(
            LikeReporte.reporte_id == reporte.id,
            LikeReporte.usuario_id == usuario_id
        ).first() is not None

        reportes_con_likes.append(
            ReporteResponse(
                id=reporte.id,
                titulo=reporte.titulo,
                descripcion=reporte.descripcion,
                categoria_id=reporte.categoria_id,
                latitud=reporte.latitud,
                longitud=reporte.longitud,
                direccion_referencia=reporte.direccion_referencia,
                imagen_url=reporte.imagen_url,
                fecha_creacion=reporte.fecha_creacion,
                fecha_actualizacion=reporte.fecha_actualizacion,
                estado=reporte.estado.value,
                usuario_id=reporte.usuario_id,
                usuario=reporte.usuario,
                categoria=reporte.categoria,
                total_likes=total_likes,
                usuario_dio_like=usuario_dio_like,
                urgencia=reporte.urgencia.value if reporte.urgencia else "media",
                score_urgencia=reporte.score_urgencia or 0.0
            )
        )

    return ReportesPaginados(
        items=reportes_con_likes,
        page=page,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


# ============================================
# 📄 LISTAR REPORTES (con filtros y paginación)
# ============================================
@router.get("", response_model=ReportesPaginados)
def obtener_reportes(
        page: int = 1,
        per_page: int = 12,
        categoria_id: int | None = None,
        estado: str | None = None,
        search: str | None = None,
        orden: str | None = None,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
):
    usuario_id = current_user.id

    query = db.query(Reporte)

    if categoria_id:
        query = query.filter(Reporte.categoria_id == categoria_id)

    if estado:
        query = query.filter(Reporte.estado == estado)

    if search:
        query = query.filter(
            or_(
                Reporte.titulo.ilike(f"%{search}%"),
                Reporte.descripcion.ilike(f"%{search}%"),
                Reporte.direccion_referencia.ilike(f"%{search}%")
            )
        )

    # Ordenamiento
    if orden == "urgencia":
        query = query.order_by(Reporte.score_urgencia.desc())
    else:
        query = query.order_by(Reporte.fecha_creacion.desc())

    total = query.count()
    pages = max(1, (total + per_page - 1) // per_page)

    reportes = (
        query
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    # ✅ DEBUG: Ver qué likes existen en la BD
    todos_los_likes = db.query(LikeReporte).all()
    print(f"\n📊 TOTAL DE LIKES EN BD: {len(todos_los_likes)}")
    for like in todos_los_likes:
        print(f"   - Reporte {like.reporte_id} → Usuario {like.usuario_id}")
    print(f"🔍 Usuario actual buscando: {usuario_id}\n")

    reportes_con_likes = []
    for reporte in reportes:
        total_likes = db.query(func.count(LikeReporte.id)).filter(
            LikeReporte.reporte_id == reporte.id
        ).scalar() or 0

        # ← VERIFICAR SI EL USUARIO DIO LIKE
        usuario_dio_like = db.query(LikeReporte).filter(
            LikeReporte.reporte_id == reporte.id,
            LikeReporte.usuario_id == usuario_id
        ).first() is not None

        # ✅ DEBUG: Ver cada reporte
        print(f"Reporte {reporte.id}: total_likes={total_likes}, usuario_dio_like={usuario_dio_like}")

        reportes_con_likes.append(
            ReporteResponse(
                id=reporte.id,
                titulo=reporte.titulo,
                descripcion=reporte.descripcion,
                categoria_id=reporte.categoria_id,
                latitud=reporte.latitud,
                longitud=reporte.longitud,
                direccion_referencia=reporte.direccion_referencia,
                imagen_url=reporte.imagen_url,
                fecha_creacion=reporte.fecha_creacion,
                fecha_actualizacion=reporte.fecha_actualizacion,
                estado=reporte.estado.value,
                usuario_id=reporte.usuario_id,
                usuario=reporte.usuario,
                categoria=reporte.categoria,
                total_likes=total_likes,
                usuario_dio_like=usuario_dio_like
            )
        )

    return ReportesPaginados(
        items=reportes_con_likes,
        page=page,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


# ============================================
# 📝 CREAR REPORTE - CORREGIDO
# ============================================
@router.post("", response_model=ReporteResponse)
def crear_reporte(
        titulo: str = Form(...),
        descripcion: str = Form(...),
        categoria_id: int = Form(...),
        latitud: float = Form(...),
        longitud: float = Form(...),
        direccion_referencia: str | None = Form(None),
       # usuario_id: int = Form(...),
        imagen: UploadFile | None = File(None),
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)

):
    imagen_url = None

    if imagen:
        # Crear carpeta uploads/reportes (sin duplicar /uploads)
        upload_folder = os.path.join(UPLOAD_DIR, "reportes")
        os.makedirs(upload_folder, exist_ok=True)

        # Ruta completa en el disco: uploads/reportes/nombre.jpg
        file_path = os.path.join(upload_folder, imagen.filename)

        # Guardar imagen físicamente
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

        # Solo guardar el nombre del archivo en la BD
        imagen_url = imagen.filename

    nuevo = Reporte(
        titulo=titulo,
        descripcion=descripcion,
        categoria_id=categoria_id,
        latitud=latitud,
        longitud=longitud,
        direccion_referencia=direccion_referencia,
        usuario_id=current_user.id,
        imagen_url=imagen_url
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    
    # Calcular urgencia con IA
    try:
        urgencia, score = calcular_score_urgencia(nuevo, db)
        nuevo.urgencia = urgencia
        nuevo.score_urgencia = score
        db.commit()
        db.refresh(nuevo)
    except Exception as e:
        print(f"Advertencia: No se pudo calcular urgencia: {e}")

    return ReporteResponse(
        id=nuevo.id,
        titulo=nuevo.titulo,
        descripcion=nuevo.descripcion,
        categoria_id=nuevo.categoria_id,
        latitud=nuevo.latitud,
        longitud=nuevo.longitud,
        direccion_referencia=nuevo.direccion_referencia,
        imagen_url=nuevo.imagen_url,
        fecha_creacion=nuevo.fecha_creacion,
        fecha_actualizacion=nuevo.fecha_actualizacion,
        estado=nuevo.estado.value,
        usuario_id=nuevo.usuario_id,
        usuario=nuevo.usuario,
        categoria=nuevo.categoria,
        total_likes=0,
        usuario_dio_like=False,
        urgencia=nuevo.urgencia.value,
        score_urgencia=nuevo.score_urgencia
    )


# ============================================
# ❤️ TOGGLE LIKE
# ============================================
@router.post("/{id}/like")
def toggle_like(
        id: int,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)  # ← AQUÍ
):
    usuario_id = current_user.id

    # ✅ DEBUG
    print(f"\n❤️ TOGGLE LIKE - Reporte: {id}, Usuario: {usuario_id}")

    like = db.query(LikeReporte).filter(
        LikeReporte.reporte_id == id,
        LikeReporte.usuario_id == usuario_id
    ).first()

    if like:
        print(f"   ❌ Quitando like (ya existía)")
        db.delete(like)
        db.commit()
        dio_like = False
    else:
        print(f"   ✅ Agregando like (no existía)")
        nuevo = LikeReporte(reporte_id=id, usuario_id=usuario_id)
        db.add(nuevo)
        db.commit()
        dio_like = True

    total = db.query(LikeReporte).filter(LikeReporte.reporte_id == id).count()

    print(f"   📊 Total likes: {total}, usuario_dio_like: {dio_like}\n")
    
    # Recalcular urgencia después de cambio de likes
    try:
        reporte = db.query(Reporte).filter(Reporte.id == id).first()
        if reporte:
            urgencia, score = calcular_score_urgencia(reporte, db)
            reporte.urgencia = urgencia
            reporte.score_urgencia = score
            db.commit()
    except Exception as e:
        print(f"Advertencia: No se pudo recalcular urgencia: {e}")

    return {
        "usuario_dio_like": dio_like,
        "total_likes": total
    }

# ============================================
# 🔥 OBTENER REPORTE POR ID (AL FINAL)
# ============================================
@router.get("/detalle/{id}", response_model=ReporteResponse)
def obtener_reporte(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    reporte = (
        db.query(Reporte)
        .join(Usuario)
        .join(Categoria)
        .filter(Reporte.id == id)
        .first()
    )

    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    usuario_id = current_user.id

    total_likes = db.query(func.count(LikeReporte.id)).filter(
        LikeReporte.reporte_id == reporte.id
    ).scalar() or 0

    usuario_dio_like = db.query(LikeReporte).filter(
        LikeReporte.reporte_id == reporte.id,
        LikeReporte.usuario_id == usuario_id
    ).first() is not None

    return ReporteResponse(
        id=reporte.id,
        titulo=reporte.titulo,
        descripcion=reporte.descripcion,
        categoria_id=reporte.categoria_id,
        latitud=reporte.latitud,
        longitud=reporte.longitud,
        direccion_referencia=reporte.direccion_referencia,
        imagen_url=reporte.imagen_url,
        fecha_creacion=reporte.fecha_creacion,
        fecha_actualizacion=reporte.fecha_actualizacion,
        estado=reporte.estado.value,
        usuario_id=reporte.usuario_id,
        usuario=reporte.usuario,
        categoria=reporte.categoria,
        total_likes=total_likes,
        usuario_dio_like=usuario_dio_like,
        urgencia=reporte.urgencia.value if reporte.urgencia else "media",
        score_urgencia=reporte.score_urgencia or 0.0
    )


# ============================================
# 🚨 RECALCULAR URGENCIAS (Admin)
# ============================================
@router.post("/admin/recalcular-urgencias")
def recalcular_urgencias(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Recalcula la urgencia de los últimos N reportes"""
    # Verificar que es admin
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden hacer esto")
    
    from services.urgencia_service import recalcular_urgencias_batch
    count = recalcular_urgencias_batch(db, limit)
    
    return {"mensaje": f"Se recalcularon {count} reportes"}


# Agregar estos endpoints en reportes.py

# ============================================
# ✏️ ACTUALIZAR REPORTE
# ============================================
@router.put("/{id}", response_model=ReporteResponse)
def actualizar_reporte(
        id: int,
        titulo: str = Form(None),
        descripcion: str = Form(None),
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
):
    """Actualizar título y descripción del reporte (solo el creador)"""
    reporte = db.query(Reporte).filter(Reporte.id == id).first()

    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    # Verificar que el usuario es el creador
    if reporte.usuario_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Solo el creador puede editar este reporte"
        )

    # Actualizar campos
    if titulo:
        reporte.titulo = titulo
    if descripcion:
        reporte.descripcion = descripcion

    db.commit()
    db.refresh(reporte)

    # Obtener likes
    total_likes = db.query(func.count(LikeReporte.id)).filter(
        LikeReporte.reporte_id == reporte.id
    ).scalar() or 0

    usuario_dio_like = db.query(LikeReporte).filter(
        LikeReporte.reporte_id == reporte.id,
        LikeReporte.usuario_id == current_user.id
    ).first() is not None

    return ReporteResponse(
        id=reporte.id,
        titulo=reporte.titulo,
        descripcion=reporte.descripcion,
        categoria_id=reporte.categoria_id,
        latitud=reporte.latitud,
        longitud=reporte.longitud,
        direccion_referencia=reporte.direccion_referencia,
        imagen_url=reporte.imagen_url,
        fecha_creacion=reporte.fecha_creacion,
        fecha_actualizacion=reporte.fecha_actualizacion,
        estado=reporte.estado.value,
        usuario_id=reporte.usuario_id,
        usuario=reporte.usuario,
        categoria=reporte.categoria,
        total_likes=total_likes,
        usuario_dio_like=usuario_dio_like
    )


# ============================================
# 🗑️ ELIMINAR REPORTE
# ============================================
@router.delete("/{id}")
def eliminar_reporte(
        id: int,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
):
    """Eliminar un reporte (solo el creador)"""
    reporte = db.query(Reporte).filter(Reporte.id == id).first()

    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    # Verificar que el usuario es el creador
    if reporte.usuario_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Solo el creador puede eliminar este reporte"
        )

    # Eliminar la imagen si existe
    if reporte.imagen_url:
        imagen_path = os.path.join(UPLOAD_DIR, "reportes", reporte.imagen_url)
        if os.path.exists(imagen_path):
            os.remove(imagen_path)

    db.delete(reporte)
    db.commit()

    return {"mensaje": "Reporte eliminado exitosamente"}