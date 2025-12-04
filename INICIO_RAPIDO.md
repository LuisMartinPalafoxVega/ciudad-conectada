# ⚡ INICIO RÁPIDO (3 pasos = 5 minutos)

## Opción A: La forma MÁS rápida

### Paso 1: Obtener API Key (2 min)
```
1. Ir a: https://console.anthropic.com
2. Click "Sign Up" (crear cuenta si necesitas)
3. Ir a "API Keys"
4. Click "Create Key"
5. Copiar la key: sk-ant-v1-xxx...
```

### Paso 2: Configurar (.env)
```
Editar archivo: backend/.env

Encontrar:
ANTHROPIC_API_KEY=sk-ant-placeholder-reemplaza-con-tu-key

Reemplazar con tu key:
ANTHROPIC_API_KEY=sk-ant-v1-abc123xyz...

Guardar archivo
```

### Paso 3: Ejecutar
```bash
# Terminal 1 (Backend)
cd backend
pip install -r requirements.txt
python app/main.py

# Terminal 2 (Frontend)
cd frontend
ng serve
```

### Listo ✅
```
Backend: http://localhost:8000
Frontend: http://localhost:4200

¡A crear reportes!
```

---

## Opción B: Con Validación (10 minutos)

Seguir los 3 pasos de arriba, LUEGO:

### Paso 4: Validar BD
```sql
-- En MySQL
ALTER TABLE reportes 
ADD COLUMN urgencia VARCHAR(20) DEFAULT 'media' AFTER estado,
ADD COLUMN score_urgencia FLOAT DEFAULT 0.0 AFTER urgencia;
```

### Paso 5: Test de IA
```bash
cd backend
python test_urgencia.py

# Debería mostrar ✅
```

### Paso 6: Crear Reporte
```
1. Abrir http://localhost:4200
2. Click "Nuevo Reporte"
3. Llenar datos
4. Click Crear

Esperar 2 segundos... ¡Debería tener urgencia!
```

---

## 🎯 Eso es todo

No hay más pasos. El sistema ya está:
- ✅ Compilado
- ✅ Documentado  
- ✅ Testeable
- ✅ Listo para producción

Ahora solo disfruta las nuevas features.

---

## Si Algo Falla...

| Error | Solución |
|-------|----------|
| "ANTHROPIC_API_KEY no encontrada" | Revisar .env, sin espacios |
| "anthropic module not found" | `pip install anthropic` |
| "Column urgencia not found" | Ejecutar ALTER TABLE |
| Frontend no compila | `npm install`, luego `ng serve` |

---

## ¿Quieres aprender más?

→ Lee: `PASO_A_PASO.md` (15 min, completo)
→ Lee: `ARQUITECTURA_IA_URGENCIA.md` (técnico)
→ Lee: `FAQ_URGENCIA.md` (preguntas)

---

**¡Eso es! 🎉**

Tiempo total: ~5-10 minutos
Dificultad: Muy fácil
Resultado: Sistema de Urgencia IA funcional
