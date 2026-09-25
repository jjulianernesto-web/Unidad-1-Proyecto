"""
repositories/producto_repo.py – Acceso a datos de productos.
"""
from db.database import get_connection
from models import Producto


def _map(r) -> Producto:
    return Producto(
        r["id"], r["codigo"], r["nombre"], r["categoria_id"],
        r["cat_nombre"], r["precio"], r["stock"], bool(r["activo"])
    )


_JOIN = """
    SELECT p.*, c.nombre AS cat_nombre
    FROM productos p
    JOIN categorias c ON c.id = p.categoria_id
"""


def get_all(solo_activos: bool = False, buscar: str = "") -> list[Producto]:
    conn = get_connection()
    sql = _JOIN
    params: list = []
    conds: list[str] = []
    if solo_activos:
        conds.append("p.activo=1")
    if buscar:
        conds.append("(p.nombre LIKE ? OR p.codigo LIKE ? OR c.nombre LIKE ?)")
        params += [f"%{buscar}%", f"%{buscar}%", f"%{buscar}%"]
    if conds:
        sql += " WHERE " + " AND ".join(conds)
    sql += " ORDER BY p.nombre"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [_map(r) for r in rows]


def get_by_id(pid: int) -> Producto | None:
    conn = get_connection()
    row = conn.execute(_JOIN + " WHERE p.id=?", (pid,)).fetchone()
    conn.close()
    return _map(row) if row else None


def get_by_codigo(codigo: str) -> Producto | None:
    conn = get_connection()
    row = conn.execute(_JOIN + " WHERE p.codigo=?", (codigo,)).fetchone()
    conn.close()
    return _map(row) if row else None


def create(codigo: str, nombre: str, categoria_id: int, precio: float, stock: int) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO productos (codigo, nombre, categoria_id, precio, stock) VALUES (?,?,?,?,?)",
        (codigo, nombre, categoria_id, precio, stock),
    )
    conn.commit()
    conn.close()


def update(pid: int, codigo: str, nombre: str, categoria_id: int, precio: float, stock: int) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE productos SET codigo=?, nombre=?, categoria_id=?, precio=?, stock=? WHERE id=?",
        (codigo, nombre, categoria_id, precio, stock, pid),
    )
    conn.commit()
    conn.close()


def toggle_activo(pid: int, activo: bool) -> None:
    conn = get_connection()
    conn.execute("UPDATE productos SET activo=? WHERE id=?", (1 if activo else 0, pid))
    conn.commit()
    conn.close()


def descontar_stock(pid: int, cantidad: int, conn=None) -> None:
    """Descuenta stock; reutiliza conexión si se pasa (transacción)."""
    own = conn is None
    if own:
        conn = get_connection()
    conn.execute("UPDATE productos SET stock = stock - ? WHERE id=?", (cantidad, pid))
    if own:
        conn.commit()
        conn.close()


def tiene_ventas(pid: int) -> bool:
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM detalle_venta WHERE producto_id=?", (pid,)
    ).fetchone()[0]
    conn.close()
    return count > 0


def stock_bajo(umbral: int = 5) -> list[Producto]:
    conn = get_connection()
    rows = conn.execute(
        _JOIN + " WHERE p.activo=1 AND p.stock <= ? ORDER BY p.stock", (umbral,)
    ).fetchall()
    conn.close()
    return [_map(r) for r in rows]


def mas_vendidos(limite: int = 10) -> list[dict]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.codigo, p.nombre, c.nombre AS categoria,
               SUM(dv.cantidad) AS total_vendido,
               SUM(dv.subtotal) AS ingresos
        FROM detalle_venta dv
        JOIN productos p ON p.id = dv.producto_id
        JOIN categorias c ON c.id = p.categoria_id
        GROUP BY p.id
        ORDER BY total_vendido DESC
        LIMIT ?
    """, (limite,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
