"""
services/venta_service.py – Reglas de negocio para ventas.
"""
from datetime import date
from models import Venta, DetalleVenta
import repositories.venta_repo as repo
import repositories.producto_repo as prod_repo


class VentaError(Exception):
    pass


def listar(buscar: str = "") -> list[Venta]:
    return repo.get_all(buscar)


def obtener_detalle(venta_id: int) -> list[DetalleVenta]:
    return repo.get_detalle(venta_id)


def registrar_venta(usuario_id: int, items: list[dict]) -> int:
    """
    items: [{'producto_id': int, 'cantidad': int}]
    Valida stock, copia precio_unitario del catálogo y guarda en una transacción.
    """
    if not items:
        raise VentaError("La venta no tiene productos.")

    items_completos = []
    for it in items:
        pid = it["producto_id"]
        cantidad = it["cantidad"]
        producto = prod_repo.get_by_id(pid)

        if producto is None:
            raise VentaError(f"Producto con id {pid} no encontrado.")
        if not producto.activo:
            raise VentaError(f"'{producto.nombre}' está inactivo y no se puede vender.")
        if cantidad <= 0:
            raise VentaError(f"Cantidad inválida para '{producto.nombre}'.")
        if cantidad > producto.stock:
            raise VentaError(
                f"Stock insuficiente para '{producto.nombre}'. "
                f"Disponible: {producto.stock}, solicitado: {cantidad}."
            )
        items_completos.append({
            "producto_id": pid,
            "cantidad": cantidad,
            "precio_unitario": producto.precio,   # precio_unitario se copia del catálogo
        })

    fecha = date.today().isoformat()
    return repo.create_venta(fecha, usuario_id, items_completos)
