"""
models/ – Clases de dominio (sin widgets Tkinter).
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Usuario:
    id: int
    username: str
    nombre_completo: str
    rol: str
    activo: bool


@dataclass
class Categoria:
    id: int
    nombre: str
    activo: bool


@dataclass
class Producto:
    id: int
    codigo: str
    nombre: str
    categoria_id: int
    categoria_nombre: str
    precio: float
    stock: int
    activo: bool


@dataclass
class DetalleVenta:
    producto_id: int
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float


@dataclass
class Venta:
    id: int
    fecha: str
    usuario_id: int
    usuario_nombre: str
    total: float
    detalles: list = field(default_factory=list)
