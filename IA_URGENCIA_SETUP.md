# Sistema de Clasificación de Urgencia por IA - Ciudad Conectada

## 🚀 Descripción

Se ha integrado un sistema de clasificación automática de urgencia de reportes usando **Claude IA** de Anthropic. El sistema:

1. **Analiza automáticamente** cada reporte al crearlo
2. **Clasifica la urgencia** en 4 niveles: Baja, Media, Alta, Crítica
3. **Calcula un score** de urgencia (0-100) basado en:
   - Descripción y contenido del reporte
   - Categoría del problema
   - Engagement de la comunidad (likes, comentarios)

4. **Prioriza reportes urgentes** en:
   - Feed de usuarios (ordenar por urgencia)
   - Dashboard de administración (mostrar reportes críticos primero)

## 📋 Configuración Requerida

### 1. Backend - Obtener API Key de Claude

1. Ir a [console.anthropic.com](https://console.anthropic.com)
2. Crear una cuenta o iniciar sesión
3. Crear una nueva API Key
4. Copiar la key (formato: `sk-ant-...`)

### 2. Backend - Configurar Variable de Entorno

En `backend/.env`, reemplazar:
```
ANTHROPIC_API_KEY=sk-ant-placeholder-reemplaza-con-tu-key
```

Con tu API Key real:
```
ANTHROPIC_API_KEY=sk-ant-v1-xxxxxxxxxxxxxx
```

### 3. Backend - Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

Se añadió automáticamente `anthropic==0.46.0` a requirements.txt

### 4. Backend - Migración de BD (Importante)

Ejecutar estas migraciones SQL:

```sql
-- Añadir columnas a tabla reportes
ALTER TABLE reportes ADD COLUMN urgencia VARCHAR(20) DEFAULT 'media' AFTER estado;
ALTER TABLE reportes ADD COLUMN score_urgencia FLOAT DEFAULT 0.0 AFTER urgencia;
```

O en caso de usar SQLAlchemy:
```python
# Reinicializar BD (desarrollo)
python
>>> from app.database import engine, Base
>>> from models.reportes import Reporte  # Importar modelos actualizados
>>> Base.metadata.create_all(bind=engine)
```

## 🎯 Características Principales

### Frontend Usuario (Feed)

✅ **Nuevo Filtro de Ordenamiento**
- "Más reciente" (por defecto)
- "Más urgente" (ordena por score de urgencia)

✅ **Badges de Urgencia en Tarjetas**
- 🟢 **Baja** - Problemas menores
- 🟡 **Media** - Problemas moderados
- 🟠 **Alta** - Problemas graves
- 🔴 **Crítica** - Emergencias (con animación pulsante)

### Frontend Admin (Dashboard)

✅ **Nueva Columna de Urgencia** en tabla de reportes

✅ **Ordenamiento por Urgencia**
- Mostrar reportes críticos primero
- Opción en selector "Ordenar por"

✅ **Visualización Mejorada**
- Badges de color para cada nivel
- Score visible en el hover

## 🔄 Cómo Funciona la IA

### Al crear un reporte:
```
1. Usuario crea reporte con título, descripción, categoría
2. Se guarda en BD con urgencia = "media" (por defecto)
3. IA analiza automáticamente el contenido
4. Se calcula score de urgencia (0-100)
5. Se actualiza registro con urgencia real
```

### Al cambiar likes:
```
1. Usuario da like a un reporte
2. Total de likes se incrementa
3. IA recalcula urgencia considerando engagement
4. Score se actualiza automáticamente
```

### Endpoint para recalcular (Admin):
```bash
POST /reportes/admin/recalcular-urgencias?limit=50
```

Recalcula urgencia de últimos 50 reportes manualmente.

## 📊 Ejemplo de Respuesta API

```json
{
  "id": 1,
  "titulo": "Fuga de agua en Calle Principal",
  "descripcion": "...",
  "urgencia": "critica",
  "score_urgencia": 92.5,
  "estado": "pendiente",
  "total_likes": 45,
  ...
}
```

## 🚨 Niveles de Urgencia

| Nivel | Score | Descripción | Ejemplo |
|-------|-------|-------------|---------|
| **Baja** | 0-30 | Problemas menores que pueden esperar | Falta señalización, bache pequeño |
| **Media** | 31-60 | Problemas moderados que necesitan atención | Alumbrado deficiente, basura acumulada |
| **Alta** | 61-85 | Problemas graves que necesitan atención pronta | Fuga de agua, socavón grande |
| **Crítica** | 86-100 | Emergencias que ponen en riesgo vidas | Riesgo de electrocución, colapso estructural |

## 💡 Ejemplo de Uso - Usuario

```
Usuario abre app → Feed de reportes
↓
Ve opción: "Ordenar por: Más urgente"
↓
Reportes críticos aparecen primero con badge 🔴
↓
Click en reporte → Ver detalles y apoyar con like
```

## 💡 Ejemplo de Uso - Admin

```
Admin abre Dashboard → Tabla de reportes
↓
Ve nueva columna "Urgencia" con códigos de color
↓
Selecciona "Ordenar por: Más urgente"
↓
Reportes críticos en la parte superior
↓
Puede filtrar por estado + urgencia combinados
```

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY no está definida"
- ✅ Verificar que `.env` tiene `ANTHROPIC_API_KEY=sk-ant-...`
- ✅ Reiniciar servidor backend

### Error: "No se pudo calcular urgencia"
- ✅ Verificar que API Key es válida
- ✅ Verificar que tienes cuota disponible en Anthropic
- ✅ El reporte se crea igual, con urgencia = "media" por defecto

### Reportes no ordenados por urgencia
- ✅ Asegurarse que parámetro `orden=urgencia` se envía
- ✅ Verificar en Network tab del navegador

## 📝 Notas de Desarrollo

- **Modelo IA**: Claude 3.5 Sonnet (optimizado para clasificación)
- **Latencia**: ~1-2 segundos por reporte
- **Fallback**: Si falla IA, se calcula score simple por engagement
- **Caché**: Scores se recalculan cuando hay cambios significativos

## 🔐 Seguridad

- API Key nunca se envía al frontend
- Procesamiento en backend seguro
- Rate limiting en Anthropic protege quota
- Cada usuario ve información según permisos

## 📚 Recursos

- [Documentación Anthropic API](https://docs.anthropic.com)
- [Modelos disponibles](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Precios de Claude](https://www.anthropic.com/pricing)

---

**Actualizado**: Diciembre 2024  
**Versión**: 1.0.0
