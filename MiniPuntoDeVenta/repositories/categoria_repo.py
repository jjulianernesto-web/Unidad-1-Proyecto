"""
repositories/categoria_repo.py – Acceso a datos de categorías.
"""
from db.database import get_connection
from models import Categoria


def get_all(solo_activas: bool = False) -> list[Categoria]:
    conn = get_connection()
    sql = "SELECT * FROM categorias"
    if solo_activas:
        sql += " WHERE activo=1"
    sql += " ORDER BY nombre"
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [Categoria(r["id"], r["nombre"], bool(r["activo"])) for r in rows]


def get_by_id(cid: int) -> Categoria | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM categorias WHERE id=?", (cid,)).fetchone()
    conn.close()
    return Categoria(row["id"], row["nombre"], bool(row["activo"])) if row else None


def create(nombre: str) -> None:
    conn = get_connection()
    conn.execute("INSERT INTO categorias (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()


def update(cid: int, nombre: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE categorias SET nombre=? WHERE id=?", (nombre, cid))
    conn.commit()
    conn.close()


def toggle_activo(cid: int, activo: bool) -> None:
    conn = get_connection()
    conn.execute("UPDATE categorias SET activo=? WHERE id=?", (1 if activo else 0, cid))
    conn.commit()
    conn.close()


def tiene_productos_activos(cid: int) -> bool:
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM productos WHERE categoria_id=? AND activo=1", (cid,)
    ).fetchone()[0]
    conn.close()
    return count > 0
