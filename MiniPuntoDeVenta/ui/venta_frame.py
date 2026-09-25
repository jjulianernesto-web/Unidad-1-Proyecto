"""
ui/venta_frame.py – Movimiento de venta con detalle y listado con JOIN.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import BG, SURFACE, CARD, ACCENT, FG, FG2, FONT_BODY, FONT_SMALL
from ui import widgets as W
import services.venta_service as svc
import services.producto_service as prod_svc


class VentaFrame(ttk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.usuario = usuario
        self._build()
        self.cargar()

    def _build(self):
        # Notebook: Nueva venta | Historial
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self._tab_nueva    = ttk.Frame(nb)
        self._tab_historial = ttk.Frame(nb)
        nb.add(self._tab_nueva,     text="  🛒  Nueva Venta  ")
        nb.add(self._tab_historial, text="  📜  Historial  ")

        self._build_nueva(self._tab_nueva)
        self._build_historial(self._tab_historial)

    # ── Nueva venta ──────────────────────────────────────────────────────
    def _build_nueva(self, parent):
        left = ttk.Frame(parent)
        left.pack(side="left", fill="both", expand=True, padx=(0, 4))
        right = ttk.LabelFrame(parent, text="  Carrito de compra")
        right.pack(side="right", fill="both", expand=True, padx=(4, 0))

        # Buscar producto
        ttk.Label(left, text="Buscar producto").pack(anchor="w", pady=(8, 2))
        search_frame = ttk.Frame(left)
        search_frame.pack(fill="x")
        self._var_prod_buscar = tk.StringVar()
        ent = ttk.Entry(search_frame, textvariable=self._var_prod_buscar, width=28)
        ent.pack(side="left", ipady=5)
        self._var_prod_buscar.trace_add("write", lambda *_: self._buscar_productos())
        ttk.Button(search_frame, text="Agregar ➡", command=self._agregar_al_carrito).pack(
            side="left", padx=6, ipady=4)

        # Cantidad
        qty_frame = ttk.Frame(left)
        qty_frame.pack(fill="x", pady=4)
        ttk.Label(qty_frame, text="Cantidad:").pack(side="left")
        self._var_qty = tk.StringVar(value="1")
        ttk.Entry(qty_frame, textvariable=self._var_qty, width=6).pack(side="left", padx=6, ipady=4)

        # Lista de productos disponibles
        cols = [("codigo", "Código", 75), ("nombre", "Nombre", 180),
                ("precio", "Precio", 70), ("stock", "Stock", 50)]
        self._tree_prods = W.make_tree(left, cols, height=12)

        # Carrito (derecha)
        ttk.Label(right, text="Items en carrito:", style="Card.TLabel").pack(anchor="w", padx=8, pady=(6, 2))
        cart_cols = [("nombre", "Producto", 160), ("cant", "Cant.", 45),
                     ("pu", "P.Unit.", 65), ("sub", "Subtotal", 70)]
        self._tree_carrito = W.make_tree(right, cart_cols, height=10)
        self._carrito: list[dict] = []  # [{producto_id, nombre, cantidad, precio_unitario}]

        # Total
        total_f = ttk.Frame(right)
        total_f.pack(fill="x", padx=8, pady=4)
        ttk.Label(total_f, text="TOTAL:", style="Accent.TLabel").pack(side="left")
        self._lbl_total = ttk.Label(total_f, text="$0.00", style="Accent.TLabel")
        self._lbl_total.pack(side="left", padx=8)

        btn_f = ttk.Frame(right)
        btn_f.pack(fill="x", padx=8, pady=(4, 8))
        ttk.Button(btn_f, text="🗑 Quitar ítem", style="Warn.TButton",
                   command=self._quitar_item).pack(side="left", ipady=4)
        ttk.Button(btn_f, text="✅ Registrar venta", style="Success.TButton",
                   command=self._registrar).pack(side="left", padx=8, ipady=4)

        self._buscar_productos()

    def _buscar_productos(self):
        buscar = self._var_prod_buscar.get()
        prods  = prod_svc.listar(solo_activos=True, buscar=buscar)
        rows   = [(p.codigo, p.nombre, f"${p.precio:.2f}", p.stock) for p in prods]
        tags   = [("alerta" if p.stock <= 5 else ("par" if i % 2 == 0 else "impar"))
                  for i, p in enumerate(prods)]
        self._prods_disponibles = prods
        W.reload_tree(self._tree_prods, rows, tags)

    def _agregar_al_carrito(self):
        sel = self._tree_prods.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona un producto.", parent=self)
            return
        codigo = self._tree_prods.item(sel[0])["values"][0]
        prod   = next((p for p in self._prods_disponibles if p.codigo == codigo), None)
        if not prod:
            return

        try:
            qty = int(self._var_qty.get())
            if qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Cantidad inválida", "Ingresa una cantidad entera mayor a 0.", parent=self)
            return

        # Si ya está en carrito, actualizar cantidad
        existing = next((it for it in self._carrito if it["producto_id"] == prod.id), None)
        if existing:
            existing["cantidad"] += qty
        else:
            self._carrito.append({
                "producto_id": prod.id,
                "nombre": prod.nombre,
                "cantidad": qty,
                "precio_unitario": prod.precio,
            })
        self._refresh_carrito()

    def _quitar_item(self):
        sel = self._tree_carrito.selection()
        if not sel:
            return
        nombre = self._tree_carrito.item(sel[0])["values"][0]
        self._carrito = [it for it in self._carrito if it["nombre"] != nombre]
        self._refresh_carrito()

    def _refresh_carrito(self):
        rows = [(it["nombre"], it["cantidad"],
                 f"${it['precio_unitario']:.2f}",
                 f"${it['cantidad']*it['precio_unitario']:.2f}")
                for it in self._carrito]
        W.reload_tree(self._tree_carrito, rows)
        total = sum(it["cantidad"] * it["precio_unitario"] for it in self._carrito)
        self._lbl_total.config(text=f"${total:.2f}")

    def _registrar(self):
        if not self._carrito:
            messagebox.showwarning("Carrito vacío", "Agrega al menos un producto.", parent=self)
            return
        if not messagebox.askyesno("Confirmar venta",
                                   f"¿Registrar venta con {len(self._carrito)} ítem(s)?",
                                   parent=self):
            return
        try:
            items = [{"producto_id": it["producto_id"], "cantidad": it["cantidad"]}
                     for it in self._carrito]
            venta_id = svc.registrar_venta(self.usuario.id, items)
            messagebox.showinfo("Venta registrada",
                                f"✅ Venta #{venta_id} registrada exitosamente.", parent=self)
            self._carrito.clear()
            self._refresh_carrito()
            self._buscar_productos()
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error en venta", str(e), parent=self)

    # ── Historial ────────────────────────────────────────────────────────
    def _build_historial(self, parent):
        ttk.Label(parent, text="📜  Historial de Ventas", style="Accent.TLabel").pack(
            anchor="w", pady=(0, 6))
        self._var_buscar_venta = W.search_bar(parent, self.cargar)

        cols_v = [("id", "Folio", 55), ("fecha", "Fecha", 90),
                  ("usuario", "Atendió", 140), ("total", "Total", 80)]
        self._tree_ventas = W.make_tree(parent, cols_v, height=8)
        self._tree_ventas.bind("<<TreeviewSelect>>", self._mostrar_detalle)

        ttk.Label(parent, text="Detalle de la venta seleccionada:",
                  style="Muted.TLabel").pack(anchor="w", pady=(8, 2))
        cols_d = [("producto", "Producto", 200), ("cant", "Cantidad", 70),
                  ("pu", "P. Unit.", 80), ("sub", "Subtotal", 80)]
        self._tree_detalle = W.make_tree(parent, cols_d, height=6)

    def cargar(self):
        buscar = self._var_buscar_venta.get() if hasattr(self, "_var_buscar_venta") else ""
        ventas = svc.listar(buscar=buscar)
        rows   = [(v.id, v.fecha, v.usuario_nombre, f"${v.total:.2f}") for v in ventas]
        W.reload_tree(self._tree_ventas, rows)

    def _mostrar_detalle(self, _e=None):
        sel = self._tree_ventas.selection()
        if not sel:
            return
        venta_id = int(self._tree_ventas.item(sel[0])["values"][0])
        detalles  = svc.obtener_detalle(venta_id)
        rows = [(d.nombre_producto, d.cantidad,
                 f"${d.precio_unitario:.2f}", f"${d.subtotal:.2f}")
                for d in detalles]
        W.reload_tree(self._tree_detalle, rows)
