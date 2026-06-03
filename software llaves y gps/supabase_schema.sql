-- Ejecutar en Supabase: SQL Editor → New query → Run
-- Las tablas también se crean solas al iniciar la app en Render.

CREATE TABLE IF NOT EXISTS servicios_gps (
    id BIGSERIAL PRIMARY KEY,
    empresa TEXT NOT NULL CHECK (empresa IN ('mavi', 'tei')),
    codigo TEXT NOT NULL,
    ubicacion TEXT NOT NULL,
    distancia DOUBLE PRECISION NOT NULL,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    patente TEXT NOT NULL,
    fecha TEXT NOT NULL,
    notas TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS servicios_llaves (
    id BIGSERIAL PRIMARY KEY,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    patente TEXT NOT NULL,
    valor_insumos DOUBLE PRECISION NOT NULL,
    cobro_servicio DOUBLE PRECISION NOT NULL,
    fecha TEXT NOT NULL,
    notas TEXT DEFAULT '',
    created_at TEXT NOT NULL
);
