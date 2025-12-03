from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from models.categorias import Categoria

router = APIRouter(tags=["Categorías"])

# ============================================
# 📂 OBTENER CATEGORÍAS
# ============================================
@router.get("/todas")
def obtener_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return categorias

