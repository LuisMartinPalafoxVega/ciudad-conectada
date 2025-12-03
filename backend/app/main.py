from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from routers import auth, reportes, usuarios, categorias, admin, comentarios
import os

# Crear las tablas
Base.metadata.create_all(bind=engine)

# Crear la app primero
app = FastAPI(
    title="Ciudad Conectada API",
    description="Sistema de Reportes Ciudadanos",
    version="1.0.0"
)

# 1️⃣ CORS — DEBE IR INMEDIATAMENTE DESPUÉS DEL app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
        "https://ciudad-conectada-front-production.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 2️⃣ Crear carpetas de uploads
os.makedirs("uploads/reportes", exist_ok=True)
os.makedirs("uploads/avatares", exist_ok=True)

# 3️⃣ Incluir routers (IMPORTANTE: ANTES de montar archivos estáticos)
app.include_router(comentarios.router, prefix="/reportes")
app.include_router(auth.router, prefix="/auth")
app.include_router(usuarios.router, prefix="/usuarios")
app.include_router(reportes.router, prefix="/reportes")
app.include_router(categorias.router, prefix="/categorias")
app.include_router(admin.router, prefix="/admin")

# Alias
app.include_router(usuarios.router, prefix="/perfil")

# 4️⃣ Montar archivos estáticos (DESPUÉS de los routers)
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

# 5️⃣ Rutas extra
@app.get("/")
def read_root():
    return {"message": "Ciudad Conectada API", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)