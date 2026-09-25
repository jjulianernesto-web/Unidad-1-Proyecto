"""
repositories/venta_repo.py – Acceso a datos de ventas y detalle_venta.
"""
from db.database import get_connection
from models import Venta, DetalleVenta


def get_all(buscar: str = "") -> list[Venta]:
    conn = get_connection()
    sql = """
        SELECT v.*, u.nombre_completo AS usr_nombre
        FROM ventas v
        JOIN usuarios_sistema u ON u.id = v.usuario_id
    """
    params: list = []
    if buscar:
        sql += " WHERE u.nombre_completo LIKE ? OR v.fecha LIKE ? OR CAST(v.id AS TEXT) LIKE ?"
        params = [f"%{buscar}%", f"%{buscar}%", f"%{buscar}%"]
    sql += " ORDER BY v.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [
        Venta(r["id"], r["fecha"], r["usuario_id"], r["usr_nombre"], r["total"])
        for r in rows
    ]


def get_detalle(venta_id: int) -> list[DetalleVenta]:
    """JOIN obligatorio: detalle + nombre del producto + folio de venta."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT dv.*, p.nombre AS prod_nombre
        FROM detalle_venta dv
        JOIN productos p ON p.id = dv.producto_id
        WHERE dv.venta_id = ?
    """, (venta_id,)).fetchall()
    conn.close()
    return [
        DetalleVenta(r["producto_id"], r["prod_nombre"], r["cantidad"],
                     r["precio_unitario"], r["subtotal"])
        for r in rows
    ]


def create_venta(fecha: str, usuario_id: int, items: list[dict]) -> int:
    """
    items: [{'producto_id': int, 'cantidad': int, 'precio_unitario': float}]
    Devuelve el id de la nueva venta.
    """
    conn = get_connection()
    total = sum(it["cantidad"] * it["precio_unitario"] for it in items)
    cur = conn.execute(
        "INSERT INTO ventas (fecha, usuario_id, total) VALUES (?,?,?)",
        (fecha, usuario_id, total),
    )
    venta_id = cur.lastrowid
    for it in items:
        subtotal = it["cantidad"] * it["precio_unitario"]
        conn.execute(
            "INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal) "
            "VALUES (?,?,?,?,?)",
            (venta_id, it["producto_id"], it["cantidad"], it["precio_unitario"], subtotal),
        )
        # Descuento de stock en la misma transacción
        conn.execute(
            "UPDATE productos SET stock = stock - ? WHERE id=?",
            (it["cantidad"], it["producto_id"]),
        )
    conn.commit()
    conn.close()
    return venta_id
