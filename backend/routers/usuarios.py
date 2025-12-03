from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from models.usuarios import Usuario
from models.reportes import Reporte, EstadoEnum
from schemas.usuario_schema import UsuarioDetalle, UsuarioUpdate, CambiarPassword
from routers.auth import hash_password, verify_password
from dependencies import get_current_user
import shutil
import os
import time
from pathlib import Path

router = APIRouter(tags=["Usuarios"])

# Directorio para avatares
UPLOAD_DIR = "uploads"
os.makedirs(os.path.join(UPLOAD_DIR, "avatares"), exist_ok=True)


# ========================
# 🟦 Obtener perfil del usuario
# ========================
@router.get("/me", response_model=UsuarioDetalle)
def get_perfil(
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
):
    """Obtener perfil del usuario autenticado"""

    # Calcular estadísticas
    total_reportes = db.query(func.count(Reporte.id)).filter(
        Reporte.usuario_id == current_user.id
    ).scalar() or 0

    reportes_pendientes = db.query(func.count(Reporte.id)).filter(
        Reporte.usuario_id == current_user.id,
        Reporte.estado == EstadoEnum.pendiente
    ).scalar() or 0

    reportes_resueltos = db.query(func.count(Reporte.id)).filter(
        Reporte.usuario_id == current_user.id,
        Reporte.estado == EstadoEnum.resuelto
    ).scalar() or 0

    return UsuarioDetalle(
        id=current_user.id,
        nombre=current_user.nombre,
        email=current_user.email,
        rol=current_user.rol.value,
        fecha_registro=current_user.fecha_registro,
        activo=current_user.activo,
        foto_url=current_user.foto_url,
        total_reportes=total_reportes,
        reportes_pendientes=reportes_pendientes,
        reportes_resueltos=reportes_resueltos
    )


# ========================
# 🟨 Actualizar perfil
# ========================
@router.put("/me", response_model=UsuarioDetalle)
def actualizar_perfil(
        datos: UsuarioUpdate,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
):
    """Actualizar información del perfil"""

    # Actualizar campos
    if datos.nombre:
        current_user.nombre = datos.nombre

    if datos.email:
        # Verificar que el email no esté en uso
        email_existe = db.query(Usuario).filter(
            Usuario.email == datos.email,
            Usuario.id != current_user.id
        ).first()
        if email_existe:
            raise HTTPException(status_code=400, detail="El email ya está en uso")
        current_user.email = datos.email

    db.commit()
    db.refresh(current_user)

    # Recalcular estadísticas
    total_reportes = db.query(func.count(Reporte.id)).filter(
        Reporte.usuario_id == current_user.id
    ).scalar() or 0

    reportes_pendientes = db.query(func.count(Reporte.id)).filter(
        Reporte.usuario_id == current_user.id,
        Reporte.estado == EstadoEnum.pendiente
    ).scalar() or 0

    reportes_resueltos = db.query(func.count(Reporte.id)).filter(
        Reporte.usuario_id == current_user.id,
        Reporte.estado == EstadoEnum.resuelto
    ).scalar() or 0

    return UsuarioDetalle(
        id=current_user.id,
        nombre=current_user.nombre,
        email=current_user.email,
        rol=current_user.rol.value,
        fecha_registro=current_user.fecha_registro,
        activo=current_user.activo,
        foto_url=current_user.foto_url,
        total_reportes=total_reportes,
        reportes_pendientes=reportes_pendientes,
        reportes_resueltos=reportes_resueltos
    )


# ========================
# 🔒 Cambiar contraseña
# ========================
@router.put("/cambiar-password")
def cambiar_password(
        datos: CambiarPassword,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
):
    """Cambiar contraseña del usuario"""

    # Verificar contraseña actual
    if not verify_password(datos.password_actual, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

    # Actualizar contraseña
    current_user.password_hash = hash_password(datos.password_nueva)
    db.commit()

    return {"mensaje": "Contraseña actualizada exitosamente"}


# ========================
# 🖼️ Subir avatar
# ========================
@router.post("/avatar")
def subir_avatar(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
):
    """Subir foto de perfil del usuario"""

    print(f"\n📸 ========== SUBIENDO AVATAR ==========")
    print(f"👤 Usuario: {current_user.id} - {current_user.nombre}")
    print(f"📁 Archivo: {file.filename}")
    print(f"📄 Tipo: {file.content_type}")

    # Validar tipo de archivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes")

    # Validar tamaño (máximo 5MB)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    print(f"📊 Tamaño: {file_size / 1024 / 1024:.2f} MB")

    if file_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="La imagen no debe superar 5MB")

    # Crear carpeta si no existe
    avatar_dir = os.path.join(UPLOAD_DIR, "avatares")
    os.makedirs(avatar_dir, exist_ok=True)

    # Eliminar avatar anterior si existe
    if current_user.foto_url:
        old_filename = current_user.foto_url.replace("/uploads/avatares/", "")
        old_path = os.path.join(avatar_dir, old_filename)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
                print(f"🗑️ Avatar anterior eliminado: {old_path}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar avatar anterior: {e}")

    # Generar nombre único
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"avatar_{current_user.id}_{int(time.time())}.{file_extension}"
    file_path = os.path.join(avatar_dir, filename)

    print(f"💾 Guardando en: {file_path}")

    # Guardar archivo
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"✅ Archivo guardado exitosamente")
    except Exception as e:
        print(f"❌ Error al guardar archivo: {e}")
        raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {str(e)}")

    # Actualizar usuario en BD
    foto_url = f"/uploads/avatares/{filename}"
    print(f"🔄 Actualizando foto_url en BD: {foto_url}")

    try:
        current_user.foto_url = foto_url
        db.commit()
        db.refresh(current_user)
        print(f"✅ BD actualizada. Nuevo foto_url: {current_user.foto_url}")
    except Exception as e:
        print(f"❌ Error al actualizar BD: {e}")
        db.rollback()
        # Intentar eliminar el archivo guardado
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error al actualizar base de datos: {str(e)}")

    print(f"========================================\n")

    return {
        "mensaje": "Avatar actualizado correctamente",
        "url": foto_url
    }