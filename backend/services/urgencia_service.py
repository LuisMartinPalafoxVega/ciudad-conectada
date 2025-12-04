"""
Servicio de clasificación de urgencia usando Claude IA
"""
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models.reportes import Reporte, UrgenciaEnum
from models.likes import LikeReporte
from models.comentarios import Comentario
from sqlalchemy import func

# Cargar variables de entorno
load_dotenv()

# Inicializar cliente de Anthropic
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY no está definida en las variables de entorno")

client = Anthropic(api_key=api_key)

def calcular_score_urgencia(reporte: Reporte, db: Session) -> tuple[str, float]:
    """
    Calcula la urgencia de un reporte usando IA.
    
    Retorna: (nivel_urgencia: str, score: float)
    """
    
    # Contar likes y comentarios
    total_likes = db.query(func.count(LikeReporte.id)).filter(
        LikeReporte.reporte_id == reporte.id
    ).scalar() or 0
    
    total_comentarios = db.query(func.count(Comentario.id)).filter(
        Comentario.reporte_id == reporte.id
    ).scalar() or 0
    
    # Construir contexto para la IA
    prompt = f"""
Analiza el siguiente reporte ciudadano y determina su nivel de urgencia.

REPORTE:
- Título: {reporte.titulo}
- Descripción: {reporte.descripcion}
- Categoría: {reporte.categoria.nombre}
- Likes de comunidad: {total_likes}
- Comentarios: {total_comentarios}
- Estado actual: {reporte.estado.value}

Basándote en la descripción, categoría y engagement de la comunidad, clasifica este reporte en ONE de estos niveles:
- BAJA: Problemas menores que pueden esperar
- MEDIA: Problemas moderados que necesitan atención normal
- ALTA: Problemas graves que necesitan atención pronta
- CRÍTICA: Emergencias que ponen en riesgo vidas o seguridad

Responde SOLO con el nivel de urgencia (BAJA, MEDIA, ALTA o CRÍTICA) seguido de un número de 0-100 indicando el score.
Formato de respuesta: "NIVEL|SCORE" (ejemplo: "ALTA|85")
"""
    
    try:
        # Llamar a Claude
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Procesar respuesta
        respuesta = message.content[0].text.strip()
        
        # Parsear respuesta
        if "|" in respuesta:
            nivel_str, score_str = respuesta.split("|")
            nivel = nivel_str.strip().lower()
            score = float(score_str.strip())
        else:
            # Fallback si la respuesta no es del formato esperado
            nivel = "media"
            score = 50.0
        
        # Validar nivel
        nivel_valido = nivel in ["baja", "media", "alta", "critica"]
        if not nivel_valido:
            nivel = "media"
            score = 50.0
        
        return nivel, min(100.0, max(0.0, score))
        
    except Exception as e:
        print(f"Error en IA: {e}")
        # Score por defecto basado en engagement
        score = min(100.0, total_likes * 5 + total_comentarios * 3)
        if score > 70:
            return "alta", score
        elif score > 40:
            return "media", score
        else:
            return "baja", score


def actualizar_urgencia_reporte(reporte_id: int, db: Session):
    """
    Actualiza la urgencia de un reporte específico
    """
    reporte = db.query(Reporte).filter(Reporte.id == reporte_id).first()
    if not reporte:
        return None
    
    # Calcular urgencia con IA
    urgencia, score = calcular_score_urgencia(reporte, db)
    
    # Actualizar en BD
    reporte.urgencia = UrgenciaEnum(urgencia)
    reporte.score_urgencia = score
    db.commit()
    db.refresh(reporte)
    
    return reporte


def recalcular_urgencias_batch(db: Session, limit: int = 100):
    """
    Recalcula urgencias de los últimos N reportes
    """
    reportes = db.query(Reporte).order_by(
        Reporte.fecha_creacion.desc()
    ).limit(limit).all()
    
    for reporte in reportes:
        try:
            urgencia, score = calcular_score_urgencia(reporte, db)
            reporte.urgencia = UrgenciaEnum(urgencia)
            reporte.score_urgencia = score
        except Exception as e:
            print(f"Error procesando reporte {reporte.id}: {e}")
    
    db.commit()
    return len(reportes)
