"""
services/producto_service.py – Reglas de negocio para productos.
"""
from models import Producto
import repositories.producto_repo as repo


class ProductoError(Exception):
    pass


def listar(solo_activos: bool = False, buscar: str = "") -> list[Producto]:
    return repo.get_all(solo_activos, buscar)


def obtener(pid: int) -> Producto | None:
    return repo.get_by_id(pid)


def crear(codigo: str, nombre: str, categoria_id: int, precio: float, stock: int) -> None:
    codigo = codigo.strip().upper()
    nombre = nombre.strip()
    if not codigo or not nombre:
        raise ProductoError("Código y nombre son obligatorios.")
    if precio <= 0:
        raise ProductoError("El precio debe ser mayor a 0.")
    if stock < 0:
        raise ProductoError("El stock no puede ser negativo.")
    repo.create(codigo, nombre, categoria_id, precio, stock)


def editar(pid: int, codigo: str, nombre: str, categoria_id: int, precio: float, stock: int) -> None:
    codigo = codigo.strip().upper()
    nombre = nombre.strip()
    if not codigo or not nombre:
        raise ProductoError("Código y nombre son obligatorios.")
    if precio <= 0:
        raise ProductoError("El precio debe ser mayor a 0.")
    if stock < 0:
        raise ProductoError("El stock no puede ser negativo.")
    repo.update(pid, codigo, nombre, categoria_id, precio, stock)


def desactivar(pid: int) -> None:
    """No borrar – desactivar. Si tiene ventas, solo desactiva."""
    repo.toggle_activo(pid, False)


def activar(pid: int) -> None:
    repo.toggle_activo(pid, True)


def reporte_stock_bajo(umbral: int = 5) -> list[Producto]:
    return repo.stock_bajo(umbral)


def reporte_mas_vendidos(limite: int = 10) -> list[dict]:
    return repo.mas_vendidos(limite)
