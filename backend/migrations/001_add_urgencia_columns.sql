-- Migración de BD para agregar columnas de urgencia
-- Ejecutar en la base de datos: ciudad_conectada

-- ✅ PASO 1: Agregar columnas a tabla reportes
ALTER TABLE reportes 
ADD COLUMN urgencia VARCHAR(20) DEFAULT 'media' AFTER estado,
ADD COLUMN score_urgencia FLOAT DEFAULT 0.0 AFTER urgencia;

-- ✅ PASO 2: Crear índices para mejor performance en búsquedas
CREATE INDEX idx_reportes_urgencia ON reportes(urgencia);
CREATE INDEX idx_reportes_score_urgencia ON reportes(score_urgencia DESC);

-- ✅ PASO 3: Verificar que las columnas se crearon correctamente
DESCRIBE reportes;

-- Si todo está bien, deberías ver:
-- | urgencia      | varchar(20)  | YES  |     | media   |       |
-- | score_urgencia| float        | YES  |     | 0       |       |
