from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from models.comentarios import Comentario
from models.reportes import Reporte
from models.usuarios import Usuario
from schemas.comentario_schema import ComentarioCreate, ComentarioResponse
from dependencies import get_current_user

router = APIRouter(tags=["Comentarios"])


@router.post("/{reporte_id}/comentarios", response_model=ComentarioResponse)
def crear_comentario(
        reporte_id: int,
        datos: ComentarioCreate,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
):
    """Crear un nuevo comentario o respuesta"""
    print(f"\n📝 ========== CREAR COMENTARIO ==========")
    print(f"Reporte ID: {reporte_id}")
    print(f"Usuario: {current_user.nombre} (ID: {current_user.id})")
    print(f"Contenido: {datos.contenido}")
    print(f"Parent ID: {datos.parent_id}")

    reporte = db.query(Reporte).filter(Reporte.id == reporte_id).first()
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    # Si es una respuesta, verificar que el comentario padre existe
    if datos.parent_id:
        parent = db.query(Comentario).filter(Comentario.id == datos.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Comentario padre no encontrado")
        print(f"✅ Comentario padre encontrado: ID {parent.id}")

    nuevo_comentario = Comentario(
        contenido=datos.contenido,
        usuario_id=current_user.id,
        reporte_id=reporte_id,
        parent_id=datos.parent_id
    )

    db.add(nuevo_comentario)
    db.commit()
    db.refresh(nuevo_comentario)

    print(f"✅ Comentario creado: ID {nuevo_comentario.id}, Parent ID: {nuevo_comentario.parent_id}")
    print(f"==========================================\n")

    return nuevo_comentario


@router.put("/{reporte_id}/comentarios/{comentario_id}", response_model=ComentarioResponse)
def actualizar_comentario(
        reporte_id: int,
        comentario_id: int,
        datos: ComentarioCreate,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
):
    """Actualizar el contenido de un comentario"""
    comentario = db.query(Comentario).filter(
        Comentario.id == comentario_id,
        Comentario.reporte_id == reporte_id
    ).first()

    if not comentario:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    # Verificar que el usuario sea el autor
    if comentario.usuario_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Solo el autor puede editar este comentario"
        )

    comentario.contenido = datos.contenido
    db.commit()
    db.refresh(comentario)

    return comentario

@router.get("/{reporte_id}/comentarios", response_model=list[ComentarioResponse])
def listar_comentarios(reporte_id: int, db: Session = Depends(get_db)):
    """Obtener todos los comentarios de un reporte"""

    print(f"\n📥 ========== LISTAR COMENTARIOS ==========")
    print(f"Reporte ID: {reporte_id}")

    # Obtener TODOS los comentarios ordenados por ID
    comentarios = (
        db.query(Comentario)
        .filter(Comentario.reporte_id == reporte_id)
        .order_by(Comentario.id.asc())
        .all()
    )

    print(f"Total comentarios encontrados: {len(comentarios)}")
    for c in comentarios:
        print(f"  - ID: {c.id}, Parent: {c.parent_id}, Contenido: '{c.contenido[:30]}...'")

    # ✅ NO construir jerarquía en el backend, dejar que el frontend lo haga
    print(f"==========================================\n")

    return comentarios


@router.delete("/{reporte_id}/comentarios/{comentario_id}")
def eliminar_comentario(
        reporte_id: int,
        comentario_id: int,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
):
    """Eliminar un comentario o respuesta"""
    comentario = db.query(Comentario).filter(
        Comentario.id == comentario_id,
        Comentario.reporte_id == reporte_id
    ).first()

    if not comentario:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    # Verificar que el usuario sea el autor
    if comentario.usuario_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Solo el autor puede eliminar este comentario"
        )

    db.delete(comentario)
    db.commit()

    return {"mensaje": "Comentario eliminado exitosamente"}