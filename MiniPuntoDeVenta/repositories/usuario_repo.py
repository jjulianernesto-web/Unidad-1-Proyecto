"""
repositories/usuario_repo.py – Acceso a datos de usuarios_sistema.
"""
import hashlib
from typing import Optional
from db.database import get_connection
from models import Usuario


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def get_by_credentials(username: str, password: str) -> Optional[Usuario]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM usuarios_sistema WHERE username=? AND password_hash=? AND activo=1",
        (username, _hash(password)),
    ).fetchone()
    conn.close()
    if row:
        return Usuario(row["id"], row["username"], row["nombre_completo"], row["rol"], bool(row["activo"]))
    return None


def get_all() -> list[Usuario]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM usuarios_sistema ORDER BY username").fetchall()
    conn.close()
    return [Usuario(r["id"], r["username"], r["nombre_completo"], r["rol"], bool(r["activo"])) for r in rows]


def create(username: str, password: str, nombre: str, rol: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO usuarios_sistema (username, password_hash, nombre_completo, rol) VALUES (?,?,?,?)",
        (username, _hash(password), nombre, rol),
    )
    conn.commit()
    conn.close()


def toggle_activo(uid: int, activo: bool) -> None:
    conn = get_connection()
    conn.execute("UPDATE usuarios_sistema SET activo=? WHERE id=?", (1 if activo else 0, uid))
    conn.commit()
    conn.close()
