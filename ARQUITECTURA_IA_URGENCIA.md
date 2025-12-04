# 📊 Arquitectura del Sistema de Urgencia IA

## 🔄 Flujo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                      APLICACIÓN USUARIO                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CREAR REPORTE          →  FEED DE REPORTES      →  VER DETALLE │
│  ✍️ Título              │  🔍 Filtros            │  📄 Información
│  📝 Descripción         │  📊 Badges urgencia    │  ❤️ Like/Comentar
│  📍 Ubicación           │  📋 Ordenar:           │  👥 Comunidad
│  🏷️ Categoría           │    - Más reciente      │
│  📸 Imagen              │    - Más urgente ⭐    │
│                          │                        │
└─────────────────────────────────────────────────────────────────┘
          │                       │                      │
          │  POST /reportes       │  GET /reportes      GET /reportes/{id}
          │  (crear)              │  (listar)           (detalle)
          │                       │                      │
          └───────────────────────┴──────────────────────┘
                        │
                        ▼
          ┌─────────────────────────────────┐
          │    🔐 BACKEND FastAPI           │
          ├─────────────────────────────────┤
          │  POST /reportes                 │
          │  ├─ Guardar en BD               │
          │  ├─ Llamar IA (Claude)          │
          │  ├─ Calcular urgencia           │
          │  └─ Actualizar registro         │
          │                                 │
          │  GET /reportes?orden=urgencia   │
          │  ├─ Ordenar por score_urgencia  │
          │  ├─ Retornar con urgencia       │
          │  └─ Response JSON               │
          └─────────────────────────────────┘
                        │
          ┌─────────────┴─────────────┐
          │                           │
          ▼                           ▼
┌──────────────────────┐  ┌──────────────────────┐
│   🧠 CLAUDE IA       │  │   💾 BASE DE DATOS   │
│                      │  │   MySQL              │
│ Modelo: Sonnet 3.5   │  │                      │
│                      │  │ Tabla: reportes      │
│ Entrada:             │  │ ├─ id                │
│ ├─ Título reporte    │  │ ├─ titulo            │
│ ├─ Descripción       │  │ ├─ descripcion       │
│ ├─ Categoría         │  │ ├─ estado            │
│ ├─ Likes             │  │ ├─ urgencia ⭐       │
│ └─ Comentarios       │  │ ├─ score_urgencia ⭐ │
│                      │  │ └─ ...               │
│ Salida:              │  │                      │
│ ├─ Urgencia          │  │                      │
│ │  (baja/media/      │  │                      │
│ │   alta/critica)    │  │                      │
│ └─ Score (0-100)     │  │                      │
└──────────────────────┘  └──────────────────────┘
```

---

## 📱 FRONTEND - Experiencia del Usuario

### Feed (reportes/feed)
```
┌────────────────────────────────────────┐
│ REPORTES DE LA COMUNIDAD               │
├────────────────────────────────────────┤
│ 🔍 BUSCAR Y FILTRAR                    │
│ ├─ Búsqueda: [_____________________]  │
│ ├─ Categoría: [Todas ▼]                │
│ ├─ Estado: [Todos ▼]                   │
│ └─ Ordenar: [Más urgente ▼] ⭐ NUEVO   │
├────────────────────────────────────────┤
│ REPORTE 1                              │
│ ┌──────────────────────────────────┐   │
│ │  [  IMAGEN  ]  🔴 CRÍTICA ⭐    │   │  ← Badge urgencia nuevo
│ │  Pendiente                       │   │  ← Estado
│ │                                  │   │
│ │  🌊 Fugas | Bache en Av. Central │   │
│ │  Descripción del problema...     │   │
│ │  👤 Juan Pérez | 📍 Calle 5     │   │
│ │  📅 03/12/2024                   │   │
│ │  ❤️ 45  │  Ver detalles →        │   │
│ └──────────────────────────────────┘   │
│ REPORTE 2                              │
│ ┌──────────────────────────────────┐   │
│ │  [  IMAGEN  ]  🟠 ALTA ⭐        │   │
│ │  En Proceso                      │   │
│ │  ...                             │   │
│ └──────────────────────────────────┘   │
│ REPORTE 3                              │
│ ┌──────────────────────────────────┐   │
│ │  [  IMAGEN  ]  🟡 MEDIA ⭐       │   │
│ │  Pendiente                       │   │
│ │  ...                             │   │
│ └──────────────────────────────────┘   │
│                                        │
│  ← Anterior | Página 1 de 5 | Siguiente →
└────────────────────────────────────────┘

COLORES:
🟢 Baja     → Verde    (score: 0-30)
🟡 Media    → Amarillo (score: 31-60)
🟠 Alta     → Naranja  (score: 61-85)
🔴 Crítica  → Rojo     (score: 86-100) [con animación pulsante]
```

### Dashboard Admin (admin/dashboard)
```
┌──────────────────────────────────────────────┐
│ PANEL DE ADMINISTRACIÓN                      │
├──────────────────────────────────────────────┤
│ 📊 ESTADÍSTICAS                              │
│ [Total: 150] [Pendientes: 45] [En proceso: 32] [Resueltos: 73]
├──────────────────────────────────────────────┤
│ 🔧 GESTIÓN                                   │
│ Filtros: [Todos] [Pendientes] [En proceso] [Resueltos]
│ Ordenar por: [Más urgente ▼] ⭐ NUEVO        │
├──────────────────────────────────────────────┤
│ TABLA DE REPORTES                            │
├─────┬──────────────┬────────┬────────┬───────┤
│ ID  │ Título       │ Urgencia ⭐ │ Likes │ Acción│
├─────┼──────────────┼────────┼────────┼───────┤
│ #1  │ Fuga agua    │ 🔴 CRÍTICA │ 45    │ ✏️ 🗑️ │
│ #2  │ Socavón      │ 🟠 ALTA    │ 32    │ ✏️ 🗑️ │
│ #3  │ Basura       │ 🟡 MEDIA   │ 18    │ ✏️ 🗑️ │
│ #4  │ Falta señal  │ 🟢 BAJA    │ 8     │ ✏️ 🗑️ │
├─────┴──────────────┴────────┴────────┴───────┤
```

---

## 🔌 ENDPOINTS API

### Crear Reporte (Calcula urgencia automáticamente)
```bash
POST /reportes
Content-Type: multipart/form-data

Body:
  titulo: "Fuga de agua"
  descripcion: "Hay una fuga grande en la calle..."
  categoria_id: 1
  latitud: 40.7128
  longitud: -74.0060
  imagen: [archivo.jpg]

Response 200:
{
  "id": 1,
  "titulo": "Fuga de agua",
  "descripcion": "...",
  "urgencia": "critica",        ⭐ NUEVO
  "score_urgencia": 92.5,       ⭐ NUEVO
  "estado": "pendiente",
  "total_likes": 0,
  ...
}
```

### Listar Reportes (Soporta orden por urgencia)
```bash
GET /reportes?orden=urgencia&page=1&per_page=12

# Parámetros:
# - orden=urgencia   → Ordena por score DESC (más urgente primero)
# - orden=[vacío]    → Ordena por fecha DESC (más reciente primero)
# - categoria_id=1   → Filtro por categoría
# - estado=pendiente → Filtro por estado
# - search=agua      → Búsqueda en título/descripción

Response 200:
{
  "items": [
    {
      "id": 1,
      "urgencia": "critica",       ⭐ NUEVO
      "score_urgencia": 92.5,      ⭐ NUEVO
      ...
    },
    ...
  ],
  "page": 1,
  "pages": 5,
  "has_next": true,
  "has_prev": false
}
```

### Toggle Like (Recalcula urgencia)
```bash
POST /reportes/{id}/like

Response 200:
{
  "usuario_dio_like": true,
  "total_likes": 46
  
  // Backend automáticamente:
  // 1. Recalcula urgencia del reporte
  // 2. Actualiza score_urgencia en BD
}
```

### Recalcular Urgencias (Admin)
```bash
POST /reportes/admin/recalcular-urgencias?limit=50

# Recalcula urgencia de los últimos 50 reportes
# Útil si cambió la lógica de clasificación

Response 200:
{
  "mensaje": "Se recalcularon 50 reportes"
}
```

---

## 🎨 Niveles de Urgencia

| Nivel | Color | Score | Indicator | Descripción |
|-------|-------|-------|-----------|-------------|
| **Baja** | 🟢 Verde | 0-30 | `BAJA` | Problemas menores, pueden esperar |
| **Media** | 🟡 Amarillo | 31-60 | `MEDIA` | Problemas moderados |
| **Alta** | 🟠 Naranja | 61-85 | `ALTA` | Problemas graves |
| **Crítica** | 🔴 Rojo | 86-100 | `🚨 CRÍTICA` | Emergencias pulsantes |

---

## 🤖 Lógica de IA (Claude)

### Análisis Realizado
```
1. CONTENIDO: Analiza título + descripción
   ├─ Palabras clave: "fuga", "electrocución", "riesgo", etc.
   ├─ Severidad del problema descrito
   └─ Impacto en la comunidad

2. CATEGORÍA: Considera el tipo de problema
   ├─ Fugas de agua → posible urgencia alta
   ├─ Baches → urgencia variable
   ├─ Luminarias → urgencia media-baja
   └─ Basura → urgencia baja

3. ENGAGEMENT: Peso de participación comunitaria
   ├─ Likes: cada like suma a urgencia
   ├─ Comentarios: evidencia de interés
   └─ Edad del reporte: reportes viejos pueden bajar en urgencia

4. FACTORES COMBINADOS: Claude integra todo
   └─ Genera score final (0-100) y nivel (baja/media/alta/crítica)
```

### Ejemplo de Clasificación
```
Input:
  Título: "¡RIESGO! Contacto eléctrico en poste"
  Descripción: "El poste está mojado y hay riesgo de electrocución"
  Categoría: Luminaria
  Likes: 12
  Comentarios: 8

Claude Response:
  "CRITICA|89"
  
Output:
  urgencia: "critica"
  score_urgencia: 89.0
```

---

## 🚀 Stack Tecnológico

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- MySQL Database
- Anthropic Claude API

**Frontend:**
- Angular (TypeScript)
- Standalone Components
- RxJS Services
- CSS3 Animations

**Infraestructura:**
- Railway (Production)
- Docker (Containerized)

---

## 📈 Casos de Uso

### Caso 1: Usuario Nuevo
```
1. Abre Feed → Ve reportes más urgentes primero
2. Ve badge 🔴 en reporte crítico
3. Hace click → Ve detalles completos
4. Da like → Urgencia se recalcula automáticamente
```

### Caso 2: Admin Gestiona Recursos
```
1. Abre Dashboard → Ve reportes ordenados por urgencia
2. Resuelve reportes críticos primero
3. Cambia estado → Sistema mantiene urgencia para referencia
4. Analiza patrones de urgencia por categoría
```

### Caso 3: Análisis de Datos
```
1. Admin usa Dashboard para detectar "hot spots"
2. Ve qué zonas tienen más reportes críticos
3. Asigna recursos según urgencia
4. Monitorea mejora con tiempo
```

---

**Última actualización: Diciembre 2024**
