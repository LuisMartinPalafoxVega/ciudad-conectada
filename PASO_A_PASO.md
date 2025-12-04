# 🎯 INSTRUCCIONES PASO A PASO - Puesta en Marcha

## ⏱️ Tiempo Estimado: 10-15 minutos

---

## PASO 1️⃣ - Obtener Credenciales de IA (2 min)

### 1.1 Crear cuenta en Anthropic
- Ir a https://console.anthropic.com
- Click en "Sign Up"
- Registrarse con email
- Verificar email

### 1.2 Obtener API Key
- Ir a "API Keys" en el menú
- Click en "Create Key"
- Copiar la key completa: `sk-ant-v1-...`
- Guardar en un lugar seguro

---

## PASO 2️⃣ - Configurar Backend (3 min)

### 2.1 Editar archivo `.env`
```bash
cd backend
# Abrir archivo: .env
```

Encontrar esta línea:
```
ANTHROPIC_API_KEY=sk-ant-placeholder-reemplaza-con-tu-key
```

Reemplazar con tu key real:
```
ANTHROPIC_API_KEY=sk-ant-v1-abc123def456...
```

**⚠️ Importante:** Sin espacios, exacto igual a la copia

### 2.2 Instalar dependencias
```bash
pip install -r requirements.txt
```

Debería instalar `anthropic==0.46.0` entre otros

### 2.3 Probar conexión
```bash
python test_urgencia.py
```

Debería ver:
```
✅ ANTHROPIC_API_KEY encontrada
✅ Librería anthropic importada correctamente
✅ Cliente de Anthropic inicializado
✅ Conexión exitosa a Claude API!
✅ ¡Sistema de IA listo para usar!
```

Si ves error, revisar:
- ¿API Key es correcta? (sin espacios)
- ¿Tienes conexión a internet?
- ¿Tienes crédito en Anthropic? (primero son gratis $5)

---

## PASO 3️⃣ - Actualizar Base de Datos (3 min)

### 3.1 Abrir MySQL
```bash
# Opción 1: MySQL Workbench
# Opción 2: Línea de comandos:
mysql -u root -p
# Ingresar password
```

### 3.2 Seleccionar BD
```sql
USE ciudad_conectada;
```

### 3.3 Ejecutar migraciones
```sql
-- Comando 1: Agregar columnas
ALTER TABLE reportes 
ADD COLUMN urgencia VARCHAR(20) DEFAULT 'media' AFTER estado,
ADD COLUMN score_urgencia FLOAT DEFAULT 0.0 AFTER urgencia;

-- Comando 2: Crear índices (opcional pero recomendado)
CREATE INDEX idx_reportes_urgencia ON reportes(urgencia);
CREATE INDEX idx_reportes_score_urgencia ON reportes(score_urgencia DESC);

-- Comando 3: Verificar
DESCRIBE reportes;
```

Si todo está bien, deberías ver dos columnas nuevas:
```
| urgencia      | varchar(20)  | ...
| score_urgencia| float        | ...
```

---

## PASO 4️⃣ - Reiniciar Servidores (2 min)

### 4.1 Backend
```bash
# Terminal 1
cd backend
python app/main.py

# O si usas uvicorn:
uvicorn app.main:app --reload
```

Debería ver:
```
INFO:     Application startup complete
Uvicorn running on http://127.0.0.1:8000
```

### 4.2 Frontend
```bash
# Terminal 2
cd frontend
ng serve
```

Debería ver:
```
✔ Compiled successfully.
Application bundle generated successfully
```

---

## PASO 5️⃣ - Probar en la Aplicación (2 min)

### 5.1 Crear un reporte
1. Abrir http://localhost:4200
2. Click en "➕ Nuevo Reporte" (si estás logueado)
3. Llenar datos:
   - Título: "Fuga de agua en Calle Principal"
   - Descripción: "Hay una fuga grande que está dañando el pavimento"
   - Categoría: Agua
   - Ubicación: Tu ubicación
   - Foto: (opcional)
4. Click en "Crear Reporte"

### 5.2 Verificar urgencia
1. El reporte debería aparecer con:
   - Badge: 🔴 CRÍTICA o 🟠 ALTA (según descripción)
   - Score: número entre 0-100
2. Si tarda mucho, esperar ~2 segundos (IA procesando)

### 5.3 Ver en Feed
1. Ir a "Reportes" → Feed
2. Cambiar filtro: "Ordenar por: Más urgente"
3. El reporte creado debería estar en top (si tiene urgencia alta)

### 5.4 Ver en Admin
1. Ir a Admin Dashboard (si tienes rol admin)
2. Ver tabla con columna "URGENCIA"
3. Cambiar "Ordenar por: Más urgente"
4. Reportes se ordenan por score descendente

---

## ✅ CHECKLIST DE VALIDACIÓN

Marcar cuando cada paso esté completo:

- [ ] API Key de Anthropic obtenida
- [ ] `.env` actualizado con API Key
- [ ] `pip install -r requirements.txt` ejecutado
- [ ] `python test_urgencia.py` pasó exitosamente
- [ ] Base de datos migrada (columnas urgencia creadas)
- [ ] Backend iniciado sin errores
- [ ] Frontend compilado sin errores
- [ ] Creé un reporte de prueba
- [ ] Reporte tiene badge de urgencia
- [ ] Feed permite "Ordenar por: Más urgente"
- [ ] Admin Dashboard muestra columna Urgencia

---

## 🎯 RESULT ESPERADO

### En Feed de Usuarios
```
[ORDENAR: Más urgente ▼]  ← Nueva opción

Reporte 1: 🔴 CRÍTICA "Fuga de agua" - 92 pts
Reporte 2: 🟠 ALTA "Socavón" - 78 pts
Reporte 3: 🟡 MEDIA "Bache" - 45 pts
Reporte 4: 🟢 BAJA "Señalización" - 25 pts
```

### En Dashboard Admin
```
┌─────┬──────────┬────────────┬────────┐
│ ID  │ Título   │ URGENCIA   │ ESTADO │
├─────┼──────────┼────────────┼────────┤
│ #5  │ Fuga     │ 🔴 CRÍTICA │ ...    │
│ #3  │ Socavón  │ 🟠 ALTA    │ ...    │
│ #2  │ Bache    │ 🟡 MEDIA   │ ...    │
│ #1  │ Señales  │ 🟢 BAJA    │ ...    │
└─────┴──────────┴────────────┴────────┘
```

---

## 🐛 TROUBLESHOOTING RÁPIDO

### Error: "ANTHROPIC_API_KEY no está definida"
```
1. Verificar que .env tiene la key
2. Reiniciar terminal/servidor
3. Ejecutar: python test_urgencia.py
```

### Error: "ModuleNotFoundError: anthropic"
```
pip install anthropic==0.46.0
```

### Error en BD: "Column 'urgencia' not found"
```
Ejecutar migrations SQL de nuevo
Verificar que se ejecutaron sin error
```

### Reporte se crea pero sin urgencia
```
1. Esperar 2 segundos
2. Recargar página
3. Revisar logs del backend
4. Ejecutar python test_urgencia.py
```

### Ordenar por urgencia no funciona
```
1. Verificar que en Network tab envía: orden=urgencia
2. Revisar logs del backend
3. Base de datos tiene las columnas: DESCRIBE reportes;
```

---

## 📞 SOPORTE RÁPIDO

Si algo no funciona:

1. **Revisar logs del backend:**
   ```bash
   # Buscar errores de "Urgencia" o "Anthropic"
   ```

2. **Ejecutar test:**
   ```bash
   python test_urgencia.py
   ```

3. **Verificar BD:**
   ```sql
   DESCRIBE reportes;
   -- Debe tener: urgencia, score_urgencia
   ```

4. **Revisar .env:**
   ```bash
   cat .env | grep ANTHROPIC
   # Debe mostrar key sin espacios
   ```

---

## 📚 Documentos de Referencia

- `QUICKSTART_URGENCIA.md` - Resumen rápido
- `IA_URGENCIA_SETUP.md` - Setup detallado
- `ARQUITECTURA_IA_URGENCIA.md` - Diagramas técnicos
- `FAQ_URGENCIA.md` - Preguntas y respuestas

---

## 🎉 ¡LISTO!

Si completaste todos los pasos y todo funciona:

✅ Sistema de Urgencia IA **ACTIVO**
✅ Clasificación automática **FUNCIONANDO**
✅ Frontend actualizado **MOSTRANDO URGENCIAS**
✅ Admin dashboard **PRIORIDADES VISIBLES**

**¡Ahora puedes usar las nuevas características!**

---

**Tiempo total:** ~15 minutos
**Dificultad:** Fácil (solo pasos mecánicos)
**Soporte:** Ver FAQ_URGENCIA.md o contactar dev
