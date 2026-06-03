import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
DB_PATH = Path(__file__).parent / "servicios.db"


def _use_postgres():
    return bool(DATABASE_URL)


def _pg_url():
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


@contextmanager
def get_connection():
    if _use_postgres():
        import psycopg
        from psycopg.rows import dict_row

        conn = psycopg.connect(_pg_url(), row_factory=dict_row)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def _fetchall(cur):
    rows = cur.fetchall()
    if _use_postgres():
        return [dict(r) for r in rows]
    return [dict(r) for r in rows]


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _month_bounds(anio, mes):
    anio, mes = int(anio), int(mes)
    start = f"{anio}-{mes:02d}-01"
    if mes == 12:
        end = f"{anio + 1}-01-01"
    else:
        end = f"{anio}-{mes + 1:02d}-01"
    return start, end


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        if _use_postgres():
            cur.execute("""
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
                )
            """)
            cur.execute("""
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
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS servicios_gps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empresa TEXT NOT NULL CHECK (empresa IN ('mavi', 'tei')),
                    codigo TEXT NOT NULL,
                    ubicacion TEXT NOT NULL,
                    distancia REAL NOT NULL,
                    marca TEXT NOT NULL,
                    modelo TEXT NOT NULL,
                    patente TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    notas TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS servicios_llaves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    marca TEXT NOT NULL,
                    modelo TEXT NOT NULL,
                    patente TEXT NOT NULL,
                    valor_insumos REAL NOT NULL,
                    cobro_servicio REAL NOT NULL,
                    fecha TEXT NOT NULL,
                    notas TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                )
            """)


def add_gps(empresa, codigo, ubicacion, distancia, marca, modelo, patente, fecha, notas=""):
    params = (empresa, codigo, ubicacion, distancia, marca, modelo, patente, fecha, notas, _now())
    with get_connection() as conn:
        cur = conn.cursor()
        if _use_postgres():
            cur.execute(
                """INSERT INTO servicios_gps
                   (empresa, codigo, ubicacion, distancia, marca, modelo, patente, fecha, notas, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id""",
                params,
            )
            return cur.fetchone()["id"]
        cur.execute(
            """INSERT INTO servicios_gps
               (empresa, codigo, ubicacion, distancia, marca, modelo, patente, fecha, notas, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            params,
        )
        return cur.lastrowid


def add_llaves(marca, modelo, patente, valor_insumos, cobro_servicio, fecha, notas=""):
    params = (marca, modelo, patente, valor_insumos, cobro_servicio, fecha, notas, _now())
    with get_connection() as conn:
        cur = conn.cursor()
        if _use_postgres():
            cur.execute(
                """INSERT INTO servicios_llaves
                   (marca, modelo, patente, valor_insumos, cobro_servicio, fecha, notas, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id""",
                params,
            )
            return cur.fetchone()["id"]
        cur.execute(
            """INSERT INTO servicios_llaves
               (marca, modelo, patente, valor_insumos, cobro_servicio, fecha, notas, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            params,
        )
        return cur.lastrowid


def list_gps(empresa):
    with get_connection() as conn:
        cur = conn.cursor()
        if _use_postgres():
            cur.execute(
                "SELECT * FROM servicios_gps WHERE empresa = %s ORDER BY fecha DESC, id DESC",
                (empresa,),
            )
        else:
            cur.execute(
                "SELECT * FROM servicios_gps WHERE empresa = ? ORDER BY fecha DESC, id DESC",
                (empresa,),
            )
        return _fetchall(cur)


def list_llaves():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM servicios_llaves ORDER BY fecha DESC, id DESC")
        rows = _fetchall(cur)
    for r in rows:
        r["ganancia"] = round(r["cobro_servicio"] - r["valor_insumos"], 2)
    return rows


def delete_gps(empresa, record_id):
    with get_connection() as conn:
        cur = conn.cursor()
        if _use_postgres():
            cur.execute(
                "DELETE FROM servicios_gps WHERE id = %s AND empresa = %s",
                (record_id, empresa),
            )
        else:
            cur.execute(
                "DELETE FROM servicios_gps WHERE id = ? AND empresa = ?",
                (record_id, empresa),
            )
        return cur.rowcount > 0


def delete_llaves(record_id):
    with get_connection() as conn:
        cur = conn.cursor()
        if _use_postgres():
            cur.execute("DELETE FROM servicios_llaves WHERE id = %s", (record_id,))
        else:
            cur.execute("DELETE FROM servicios_llaves WHERE id = ?", (record_id,))
        return cur.rowcount > 0


def get_gps_for_pdf(empresa, anio, mes):
    start, end = _month_bounds(anio, mes)
    with get_connection() as conn:
        cur = conn.cursor()
        if _use_postgres():
            cur.execute(
                """SELECT * FROM servicios_gps
                   WHERE empresa = %s AND fecha >= %s AND fecha < %s
                   ORDER BY fecha ASC, id ASC""",
                (empresa, start, end),
            )
        else:
            cur.execute(
                """SELECT * FROM servicios_gps
                   WHERE empresa = ? AND fecha >= ? AND fecha < ?
                   ORDER BY fecha ASC, id ASC""",
                (empresa, start, end),
            )
        return _fetchall(cur)


def get_llaves_for_pdf(anio, mes):
    start, end = _month_bounds(anio, mes)
    with get_connection() as conn:
        cur = conn.cursor()
        if _use_postgres():
            cur.execute(
                """SELECT * FROM servicios_llaves
                   WHERE fecha >= %s AND fecha < %s
                   ORDER BY fecha ASC, id ASC""",
                (start, end),
            )
        else:
            cur.execute(
                """SELECT * FROM servicios_llaves
                   WHERE fecha >= ? AND fecha < ?
                   ORDER BY fecha ASC, id ASC""",
                (start, end),
            )
        rows = _fetchall(cur)
    for r in rows:
        r["ganancia"] = round(r["cobro_servicio"] - r["valor_insumos"], 2)
    return rows
