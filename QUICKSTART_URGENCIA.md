# 🚀 Quick Start - Sistema de Urgencia IA

## ⚡ Pasos Rápidos (5 minutos)

### 1️⃣ Obtener API Key de Claude
- Ir a https://console.anthropic.com
- Crear cuenta / Iniciar sesión
- Crear nueva "API Key"
- Copiar la key: `sk-ant-v1-...`

### 2️⃣ Configurar Backend
```bash
cd backend

# Editar .env
# ANTHROPIC_API_KEY=sk-ant-v1-TU_KEY_AQUI

# Instalar dependencias (si no lo hizo)
pip install -r requirements.txt
```

### 3️⃣ Configurar Base de Datos
Ejecutar SQL en MySQL Workbench o cliente MySQL:

```sql
ALTER TABLE reportes 
ADD COLUMN urgencia VARCHAR(20) DEFAULT 'media' AFTER estado,
ADD COLUMN score_urgencia FLOAT DEFAULT 0.0 AFTER urgencia;
```

### 4️⃣ Probar Conexión
```bash
python test_urgencia.py
```

Deberías ver: ✅ ¡Sistema de IA listo para usar!

### 5️⃣ Reiniciar Servidor
```bash
# Terminar server actual (Ctrl+C)
# Luego:
ng serve  # para frontend
# En otra terminal:
python app/main.py  # para backend (o uvicorn)
```

---

## 🎯 Nuevas Características en la App

### Para Usuarios
- ✅ Opción **"Ordenar por: Más urgente"** en Feed
- ✅ Badges de urgencia en tarjetas (🟢 Baja, 🟡 Media, 🟠 Alta, 🔴 Crítica)
- ✅ Reportes urgentes se muestran primero

### Para Admins  
- ✅ Columna "Urgencia" en tabla del Dashboard
- ✅ Opción **"Ordenar por: Más urgente"** en Admin
- ✅ Reportes críticos destacados con animación

---

## 📊 Cómo Funciona

```
Usuario crea reporte
    ↓
Backend procesa con IA
    ↓
Claude analiza: título, descripción, categoría, likes
    ↓
Retorna: urgencia (baja/media/alta/crítica) + score (0-100)
    ↓
Se guarda en BD
    ↓
Frontend muestra badges y permite ordenar
```

---

## 🐛 Si Algo Falla

| Error | Solución |
|-------|----------|
| "ANTHROPIC_API_KEY no está definida" | Editar `.env` y agregar la key |
| "ModuleNotFoundError: anthropic" | Ejecutar: `pip install anthropic` |
| "API Error 401" | Verificar que la API Key es correcta |
| "Rate limit exceeded" | Esperar unos minutos y reintentar |

---

## 📁 Archivos Nuevos/Modificados

**Nuevo:**
- `/backend/services/urgencia_service.py` - Lógica de IA
- `/backend/migrations/001_add_urgencia_columns.sql` - Migración BD
- `/backend/test_urgencia.py` - Script de prueba

**Modificado:**
- `/backend/requirements.txt` - Añadido `anthropic==0.46.0`
- `/backend/.env` - Añadido `ANTHROPIC_API_KEY`
- `/backend/models/reportes.py` - Campos urgencia, score_urgencia
- `/backend/routers/reportes.py` - Lógica de clasificación
- `/frontend/src/.../feed.component.*` - Ordenar por urgencia
- `/frontend/src/.../dashboard.component.*` - Mostrar urgencia

---

## 💡 Ejemplos de Uso

**En Frontend:**
```typescript
// Ordenar por urgencia
ordenSeleccionado = 'urgencia';

// Mostrar badge
{{ getUrgenciaTexto(reporte.urgencia) }}
```

**En API:**
```
GET /reportes?orden=urgencia&page=1&per_page=12
POST /reportes - crea reporte y calcula urgencia automáticamente
POST /reportes/{id}/like - recalcula urgencia
```

---

**¡Listo para usar!** 🎉
