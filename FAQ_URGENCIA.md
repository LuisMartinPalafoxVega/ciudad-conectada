# ❓ FAQ - Sistema de Urgencia IA

## Preguntas Frecuentes

### 🚀 Setup & Instalación

**P: ¿Necesito una API Key de pago?**
R: Anthropic ofrece crédito gratis ($5) al crear la cuenta. Para uso en producción, necesitarás pagar según el uso. Claude es muy económico (~$0.003 por request).

**P: ¿Dónde obtengo la API Key?**
R: En https://console.anthropic.com → Click en "API Keys" → "Create Key" → Copiar

**P: ¿Qué pasa si no configuré la API Key?**
R: Los reportes se crean igual con `urgencia = "media"` y `score_urgencia = 0`. No fallar, solo fallback.

**P: ¿Puedo cambiar el modelo de IA?**
R: Sí. En `/backend/services/urgencia_service.py` línea ~35, cambiar:
```python
model="claude-3-5-sonnet-20241022"
# A:
model="claude-3-opus-20250219"  # Más potente pero más lento
model="claude-3-haiku-20240307"  # Más rápido pero menos preciso
```

**P: ¿Cuánto tiempo toma clasificar un reporte?**
R: ~1-2 segundos. El usuario puede esperar o recibir respuesta de creación inmediatamente.

---

### 💻 Desarrollo

**P: ¿Cómo agrego logs de IA para debugging?**
R: En `urgencia_service.py`, añadir antes de responder:
```python
print(f"DEBUG - Reporte {reporte.id}: urgencia={nivel}, score={score}")
```

**P: ¿Puedo testear sin IA?**
R: Sí. Comentar import en `reportes.py` y usar urgencia fija.

**P: ¿Cómo mejoro la precisión de clasificación?**
R: Editar el prompt en `calcular_score_urgencia()`. Más contexto = mejor resultado.

**P: ¿Qué pasa si la BD no tiene las columnas urgencia?**
R: Error: `Column 'urgencia' not found`. Ejecutar SQL migration:
```sql
ALTER TABLE reportes 
ADD COLUMN urgencia VARCHAR(20) DEFAULT 'media';
```

---

### 🎯 Features & UX

**P: ¿Por qué algunos reportes tienen urgencia "media" por defecto?**
R: La IA aún no los procesó. Espera unos segundos y recarga.

**P: ¿Puedo editar la urgencia manualmente?**
R: No (actualmente). Se recalcula automáticamente. Para permitir edición admin:
```typescript
// En dashboard.component.ts
cambiarUrgencia(reporte: Reporte, nueva: string) {
  // Implementar endpoint PATCH /reportes/{id}/urgencia
}
```

**P: ¿La urgencia se actualiza si cambio el reporte?**
R: Actualmente solo se calcula al crear y cuando hay cambios de likes. Para que se recalcule al editar:
```python
# En endpoint PUT /reportes/{id}
urgencia, score = calcular_score_urgencia(reporte, db)
reporte.urgencia = urgencia
reporte.score_urgencia = score
db.commit()
```

**P: ¿Cómo muestro el score (0-100) en la UI?**
R: Añadir al template:
```html
<div class="score-badge">{{ reporte.score_urgencia | number:'1.0-0' }}/100</div>
```

**P: ¿Puedo ordenar por fecha Y urgencia?**
R: Actualmente no. Para hacerlo, añadir en backend:
```python
if orden == "urgencia_reciente":
    query = query.order_by(Reporte.score_urgencia.desc(), Reporte.fecha_creacion.desc())
```

---

### 📊 Datos & Analytics

**P: ¿Cómo veo qué reportes son más urgentes?**
R: Dashboard Admin → Ordenar por "Más urgente" → Ver tabla ordenada.

**P: ¿Puedo hacer reportes de urgencias?**
R: Sí, agregar endpoint:
```python
@router.get("/admin/stats/urgencias")
def get_urgencia_stats(db: Session = Depends(get_db)):
    return {
        "critica": db.query(Reporte).filter(Reporte.urgencia == "critica").count(),
        "alta": ...,
        "media": ...,
        "baja": ...
    }
```

**P: ¿Cómo exporto reportes urgentes?**
R: Crear endpoint que retorna CSV:
```python
@router.get("/admin/export/criticos")
def export_criticos(db: Session = Depends(get_db)):
    # Retornar CSV con reportes críticos
```

**P: ¿Puedo ver histórico de cambios de urgencia?**
R: Sí, crear tabla `reporte_urgencia_historial` y registrar cambios.

---

### 🔐 Seguridad & Performance

**P: ¿La API Key de Claude se expone al frontend?**
R: No. Solo el backend usa la API Key. Frontend nunca la ve.

**P: ¿Cuál es el rate limit de Claude?**
R: Con crédito gratis: 5 requests/minuto. Plan pago: depende del tier.

**P: ¿Qué pasa si excedo el rate limit?**
R: Retorna error 429. Implementar retry automático:
```python
import time
for attempt in range(3):
    try:
        message = client.messages.create(...)
        break
    except RateLimitError:
        time.sleep(2 ** attempt)  # Backoff exponencial
```

**P: ¿Puedo cachear las urgencias?**
R: Sí. Guardar en Redis:
```python
cache_key = f"urgencia:{reporte.id}"
if cached := redis.get(cache_key):
    return cached
```

**P: ¿Es seguro cambiar el prompt de la IA?**
R: Sí, pero prueba bien. Malos prompts = resultados malos.

**P: ¿Qué datos ve Claude sobre mis reportes?**
R: Solo: titulo, descripcion, nombre_categoria, num_likes, num_comentarios. Nada sensible.

---

### 🐛 Troubleshooting

**P: Error: "anthropic.AuthenticationError: Unauthorized"**
R: 
```
1. Verificar ANTHROPIC_API_KEY en .env
2. Verificar que la key no tenga espacios
3. Regenerar key en console.anthropic.com
4. Reiniciar servidor backend
```

**P: Error: "anthropic.RateLimitError"**
R:
```
1. Esperar 60 segundos
2. Si persiste, bajó tu cuota
3. Ir a console.anthropic.com → Billing
4. Agregar método de pago
```

**P: Reportes se crean pero urgencia es siempre "media"**
R:
```
1. Verificar logs del backend: ¿hay errores de IA?
2. Probar: python backend/test_urgencia.py
3. Si falla, problema con API Key/conexión
```

**P: Urgencia no se actualiza al dar like**
R:
```
1. Verificar que POST /reportes/{id}/like funciona
2. Revisar código: ¿está el recalcular después del like?
3. Ver logs del servidor
```

**P: El badge de urgencia no se muestra en UI**
R:
```
1. Verificar que reporte.urgencia llega del backend
2. Abrir DevTools → Network → Ver response
3. Verificar binding en template: {{ reporte.urgencia }}
4. Verificar CSS: .badge-urgencia tiene posición absolute
```

---

### 💡 Optimizaciones

**P: ¿Cómo hago urgencia más rápida?**
R: Usar modelo más rápido:
```python
model="claude-3-haiku-20240307"  # 3x más rápido, menos preciso
```

**P: ¿Cómo mejoro el score de urgencia?**
R: Enriquecer prompt con más contexto. Ejemplo mejorado:
```python
prompt = f"""
Analiza el siguiente reporte y determina urgencia.
Considera: riesgo de vidas, impacto en servicios, cantidad de afectados.

REPORTE:
- Título: {reporte.titulo}
- Descripción: {reporte.descripcion}
- Categoría: {reporte.categoria.nombre}
- Zona: {reporte.direccion_referencia}
- Likes: {total_likes} (señal de impacto comunitario)
- Comentarios: {total_comentarios}

Escala:
- CRÍTICA: Riesgo inmediato de vidas (89-100)
- ALTA: Problema grave que no puede esperar (61-88)
- MEDIA: Problema moderado (31-60)
- BAJA: Problema menor (0-30)

Responde: NIVEL|SCORE
"""
```

**P: ¿Cómo procesaré reportes antiguos?**
R: Crear script batch:
```python
python -c "
from app.database import SessionLocal
from routers.reportes import recalcular_urgencias_batch
db = SessionLocal()
recalcular_urgencias_batch(db, limit=1000)
"
```

---

### 📱 Deployment

**P: ¿Cómo funciona en production?**
R: Igual. Solo asegurar que:
```
1. ANTHROPIC_API_KEY en variables de entorno (Railway, Heroku, etc.)
2. Database migration ejecutada en prod
3. Frontend rebuilt y deployd
```

**P: ¿Qué sucede si IA falla en producción?**
R: Los reportes se crean igual con urgencia=media. Sin impacto en UX.

**P: ¿Puedo desactivar la IA temporalmente?**
R: Sí. En `urgencia_service.py`:
```python
def calcular_score_urgencia(...):
    # return "media", 50.0  # Fallback fijo
    # ... rest of code
```

---

## 🎓 Recursos de Aprendizaje

- [Docs de Anthropic API](https://docs.anthropic.com)
- [Claude Model Cards](https://docs.anthropic.com/claude/reference/models-overview)
- [Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/intro-to-prompting)
- [API Errors](https://docs.anthropic.com/claude/reference/errors)

---

**¿Más preguntas?** Crear issue en GitHub o contactar al equipo dev.

**Última actualización:** Diciembre 2024
