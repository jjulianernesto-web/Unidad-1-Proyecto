"""
services/categoria_service.py – Reglas de negocio para categorías.
"""
from models import Categoria
import repositories.categoria_repo as repo


class CategoriaError(Exception):
    pass


def listar(solo_activas: bool = False) -> list[Categoria]:
    return repo.get_all(solo_activas)


def crear(nombre: str) -> None:
    nombre = nombre.strip()
    if not nombre:
        raise CategoriaError("El nombre de la categoría es obligatorio.")
    repo.create(nombre)


def editar(cid: int, nombre: str) -> None:
    nombre = nombre.strip()
    if not nombre:
        raise CategoriaError("El nombre de la categoría es obligatorio.")
    repo.update(cid, nombre)


def desactivar(cid: int) -> None:
    if repo.tiene_productos_activos(cid):
        raise CategoriaError(
            "No se puede desactivar: la categoría tiene productos activos. "
            "Desactívalos primero."
        )
    repo.toggle_activo(cid, False)


def activar(cid: int) -> None:
    repo.toggle_activo(cid, True)
