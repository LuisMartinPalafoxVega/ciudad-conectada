from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.usuario_schema import UsuarioCreate
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.database import get_db
from models.usuarios import Usuario
from schemas.auth_schema import LoginRequest, LoginResponse
from dependencies import get_current_user

router = APIRouter(tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "super_secret_key_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas


def hash_password(password: str) -> str:
    """Hashear contraseña"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    """Crear token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login de usuario"""

    # Buscar usuario por email
    user = db.query(Usuario).filter(Usuario.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Verificar contraseña
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta"
        )

    # Verificar que el usuario esté activo
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacta al administrador."
        )

    # Crear tokens
    access_token = create_access_token({
        "id": user.id,
        "email": user.email,
        "rol": user.rol.value
    })

    # ✅ INCLUIR foto_url en la respuesta
    return LoginResponse(
        access_token=access_token,
        refresh_token=access_token,
        token_type="bearer",
        usuario={
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email,
            "rol": user.rol.value,
            "activo": user.activo,
            "fecha_registro": user.fecha_registro,
            "foto_url": user.foto_url  # ✅ AGREGAR ESTE CAMPO
        }
    )


@router.post("/register")
def register(request: UsuarioCreate, db: Session = Depends(get_db)):
    """Registro de nuevo usuario"""

    # Verificar si el email ya existe
    existe = db.query(Usuario).filter(Usuario.email == request.email).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Crear nuevo usuario
    nuevo_usuario = Usuario(
        nombre=request.nombre,
        email=request.email,
        password_hash=hash_password(request.password)
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # Crear token automáticamente después del registro
    access_token = create_access_token({
        "id": nuevo_usuario.id,
        "email": nuevo_usuario.email,
        "rol": nuevo_usuario.rol.value
    })

    # ✅ INCLUIR foto_url en la respuesta
    return LoginResponse(
        access_token=access_token,
        refresh_token=access_token,
        token_type="bearer",
        usuario={
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "email": nuevo_usuario.email,
            "rol": nuevo_usuario.rol.value,
            "activo": nuevo_usuario.activo,
            "fecha_registro": nuevo_usuario.fecha_registro,
            "foto_url": nuevo_usuario.foto_url  # ✅ AGREGAR ESTE CAMPO
        }
    )


@router.get("/me")
def get_current_user_info(current_user: Usuario = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return {
        "id": current_user.id,
        "nombre": current_user.nombre,
        "email": current_user.email,
        "rol": current_user.rol.value,
        "activo": current_user.activo,
        "fecha_registro": current_user.fecha_registro,
        "foto_url": current_user.foto_url  # ✅ AGREGAR ESTE CAMPO
    }