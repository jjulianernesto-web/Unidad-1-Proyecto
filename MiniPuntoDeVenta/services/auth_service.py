"""
services/auth_service.py – Autenticación y gestión de usuarios.
"""
from typing import Optional
from models import Usuario
import repositories.usuario_repo as repo


class AuthError(Exception):
    pass


def login(username: str, password: str) -> Usuario:
    if not username or not password:
        raise AuthError("Usuario y contraseña son obligatorios.")
    usuario = repo.get_by_credentials(username, password)
    if not usuario:
        raise AuthError("Credenciales incorrectas o usuario inactivo.")
    return usuario


def crear_usuario(username: str, password: str, nombre: str, rol: str) -> None:
    if not username or not password or not nombre:
        raise ValueError("Todos los campos son obligatorios.")
    if rol not in ("administrador", "operador"):
        raise ValueError("Rol inválido.")
    if len(password) < 5:
        raise ValueError("La contraseña debe tener al menos 5 caracteres.")
    repo.create(username, password, nombre, rol)


def listar_usuarios() -> list[Usuario]:
    return repo.get_all()


def desactivar_usuario(uid: int) -> None:
    repo.toggle_activo(uid, False)


def activar_usuario(uid: int) -> None:
    repo.toggle_activo(uid, True)
