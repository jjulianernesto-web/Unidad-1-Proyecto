"""
database.py – Conexión, creación de tablas y datos semilla.
"""

import sqlite3
import hashlib
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "mini_pos.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db() -> None:
    """Crea tablas si no existen e inserta datos semilla."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios_sistema (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            username         TEXT    NOT NULL UNIQUE,
            password_hash    TEXT    NOT NULL,
            nombre_completo  TEXT    NOT NULL,
            rol              TEXT    NOT NULL CHECK(rol IN ('administrador','operador')),
            activo           INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS categorias (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT    NOT NULL UNIQUE,
            activo INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS productos (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo       TEXT    NOT NULL UNIQUE,
            nombre       TEXT    NOT NULL,
            categoria_id INTEGER NOT NULL REFERENCES categorias(id),
            precio       REAL    NOT NULL CHECK(precio > 0),
            stock        INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
            activo       INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha      TEXT    NOT NULL,
            usuario_id INTEGER NOT NULL REFERENCES usuarios_sistema(id),
            total      REAL    NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS detalle_venta (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id         INTEGER NOT NULL REFERENCES ventas(id),
            producto_id      INTEGER NOT NULL REFERENCES productos(id),
            cantidad         INTEGER NOT NULL CHECK(cantidad > 0),
            precio_unitario  REAL    NOT NULL,
            subtotal         REAL    NOT NULL
        );
    """)

    # Semilla: usuarios
    admin_hash = _hash("admin123")
    op_hash = _hash("op123")
    cur.execute(
        "INSERT OR IGNORE INTO usuarios_sistema (username, password_hash, nombre_completo, rol) "
        "VALUES (?, ?, ?, ?)",
        ("admin", admin_hash, "Administrador del Sistema", "administrador"),
    )
    cur.execute(
        "INSERT OR IGNORE INTO usuarios_sistema (username, password_hash, nombre_completo, rol) "
        "VALUES (?, ?, ?, ?)",
        ("operador1", op_hash, "Juan Pérez", "operador"),
    )

    # Semilla: categorías
    cats = [
        ("Papelería",), ("Bebidas",), ("Snacks",), ("Útiles escolares",),
        ("Electrónica",),
    ]
    cur.executemany("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", cats)

    # Semilla: productos (≥8)
    productos = [
        ("LAPIZ01", "Lápiz #2 Mongol", 1, 5.00, 120),
        ("CUA01",   "Cuaderno universitario 100 h", 4, 32.00, 45),
        ("BOLT01",  "Bolígrafo azul Bic", 1, 8.50, 200),
        ("BOLT02",  "Bolígrafo rojo Bic", 1, 8.50, 180),
        ("WAT01",   "Agua 600 ml",             2, 15.00, 4),   # stock bajo
        ("COL01",   "Refresco cola 355 ml",    2, 18.00, 60),
        ("CHIP01",  "Papas fritas 45 g",       3, 16.00, 3),   # stock bajo
        ("USB01",   "USB 16 GB Kingston",      5, 145.00, 12),
        ("GOM01",   "Goma blanca Pelikan",     1, 4.00, 90),
        ("REG01",   "Regla 30 cm transparente",4, 12.00, 0),   # stock 0
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, precio, stock) VALUES (?,?,?,?,?)",
        productos,
    )

    # Marcar REG01 como inactivo (sin stock, fuera de catálogo)
    cur.execute("UPDATE productos SET activo=0 WHERE codigo='REG01'")

    # Semilla: ventas y detalles (≥3 movimientos)
    # Venta 1 – cerrada (productos entregados)
    cur.execute(
        "INSERT OR IGNORE INTO ventas (id, fecha, usuario_id, total) VALUES (1,'2026-09-20',1,61.50)"
    )
    cur.executemany(
        "INSERT OR IGNORE INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
        [
            (1, 1, 3, 5.00, 15.00),   # 3 lápices
            (1, 7, 1, 16.00, 16.00),  # 1 papas
            (1, 6, 1, 18.00, 18.00),  # 1 refresco
            (1, 9, 3, 4.00, 12.00),   # 3 gomas
        ],
    )

    # Venta 2 – vigente (hoy)
    cur.execute(
        "INSERT OR IGNORE INTO ventas (id, fecha, usuario_id, total) VALUES (2, date('now'), 2, 153.50)"
    )
    cur.executemany(
        "INSERT OR IGNORE INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
        [
            (2, 2, 1, 32.00, 32.00),   # cuaderno
            (2, 8, 1, 145.00, 145.00), # USB
        ],
    )

    # Venta 3 – stock bajo visible en reporte
    cur.execute(
        "INSERT OR IGNORE INTO ventas (id, fecha, usuario_id, total) VALUES (3,'2026-09-22',1,48.00)"
    )
    cur.executemany(
        "INSERT OR IGNORE INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
        [
            (3, 5, 8, 15.00, 120.00),  # agua – bajó stock a 4
            (3, 7, 7, 16.00, 112.00),  # papas – bajó stock a 3
        ],
    )

    conn.commit()
    conn.close()
