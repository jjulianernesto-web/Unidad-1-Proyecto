"""
ui/producto_frame.py – CRUD de productos con Treeview y formulario Toplevel.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from sqlite3 import IntegrityError
from ui.theme import BG, SURFACE, CARD, ACCENT, FG, FONT_HEADER
from ui import widgets as W
import services.producto_service as svc
import services.categoria_service as cat_svc


class ProductoFrame(ttk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.usuario = usuario
        self._build()
        self.cargar()

    def _build(self):
        ttk.Label(self, text="📦  Productos", style="Accent.TLabel").pack(anchor="w", pady=(0, 8))
        self._var_buscar = W.search_bar(self, self.cargar)

        cols = [
            ("codigo", "Código", 80),
            ("nombre", "Nombre", 200),
            ("categoria", "Categoría", 110),
            ("precio", "Precio $", 75),
            ("stock", "Stock", 55),
            ("estado", "Estado", 70),
        ]
        self._tree = W.make_tree(self, cols, height=15)

        is_admin = self.usuario.rol == "administrador"
        acciones = [("➕ Nuevo", "TButton", self._nuevo)]
        if is_admin:
            acciones += [
                ("✏️ Editar", "TButton", self._editar),
                ("🚫 Desactivar", "Warn.TButton", self._desactivar),
                ("✅ Activar", "Success.TButton", self._activar),
            ]
        W.action_bar(self, acciones)

    def cargar(self):
        buscar = self._var_buscar.get()
        prods = svc.listar(buscar=buscar)
        rows = [
            (p.codigo, p.nombre, p.categoria_nombre,
             f"${p.precio:.2f}", p.stock,
             "Activo" if p.activo else "Inactivo")
            for p in prods
        ]
        tags = []
        for p in prods:
            if not p.activo:
                tags.append("alerta")
            elif p.stock <= 5:
                tags.append("alerta")
            else:
                tags.append("ok")
        W.reload_tree(self._tree, rows, tags)

    def _get_selected_id(self) -> int | None:
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona un producto.", parent=self)
            return None
        codigo = self._tree.item(sel[0])["values"][0]
        prod = next((p for p in svc.listar() if p.codigo == codigo), None)
        return prod.id if prod else None

    def _nuevo(self):
        _FormProducto(self, None)

    def _editar(self):
        pid = self._get_selected_id()
        if pid:
            _FormProducto(self, pid)

    def _desactivar(self):
        pid = self._get_selected_id()
        if not pid:
            return
        if not messagebox.askyesno("Confirmar", "¿Desactivar este producto?", parent=self):
            return
        try:
            svc.desactivar(pid)
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _activar(self):
        pid = self._get_selected_id()
        if not pid:
            return
        try:
            svc.activar(pid)
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)


class _FormProducto(tk.Toplevel):
    def __init__(self, parent: ProductoFrame, pid: int | None):
        super().__init__(parent)
        self._parent = parent
        self._pid = pid
        self.title("Nuevo producto" if pid is None else "Editar producto")
        self.resizable(False, False)
        self.configure(bg=SURFACE)
        self.grab_set()

        self._cats = cat_svc.listar(solo_activas=True)
        self._cat_names = [c.nombre for c in self._cats]

        self._build()
        if pid:
            p = svc.obtener(pid)
            if p:
                self._var_codigo.set(p.codigo)
                self._var_nombre.set(p.nombre)
                self._var_precio.set(str(p.precio))
                self._var_stock.set(str(p.stock))
                cat = next((c for c in self._cats if c.id == p.categoria_id), None)
                if cat:
                    self._var_cat.set(cat.nombre)
        self.eval(f"tk::PlaceWindow {self} center")

    def _build(self):
        frame = tk.Frame(self, bg=SURFACE, padx=28, pady=24)
        frame.pack()
        frame.columnconfigure(1, weight=1)

        self._var_codigo = tk.StringVar()
        self._var_nombre = tk.StringVar()
        self._var_cat    = tk.StringVar()
        self._var_precio = tk.StringVar()
        self._var_stock  = tk.StringVar()

        W.labeled_entry(frame, "Código *", self._var_codigo, 0, width=24)
        W.labeled_entry(frame, "Nombre *", self._var_nombre, 1, width=24)
        W.labeled_combo(frame, "Categoría *", self._var_cat, self._cat_names, 2, width=22)
        W.labeled_entry(frame, "Precio ($) *", self._var_precio, 3, width=24)
        W.labeled_entry(frame, "Stock *", self._var_stock, 4, width=24)

        self._lbl_err = tk.Label(frame, text="", bg=SURFACE, fg="#e74c3c",
                                 font=("Segoe UI", 9), wraplength=260)
        self._lbl_err.grid(row=5, column=0, columnspan=2, pady=(8, 4))

        ttk.Button(frame, text="💾 Guardar", command=self._guardar).grid(
            row=6, column=0, columnspan=2, ipadx=10, ipady=6, sticky="ew")

    def _guardar(self):
        self._lbl_err.config(text="")
        try:
            codigo   = self._var_codigo.get()
            nombre   = self._var_nombre.get()
            cat_name = self._var_cat.get()
            precio_s = self._var_precio.get()
            stock_s  = self._var_stock.get()

            if not cat_name:
                raise ValueError("Selecciona una categoría.")
            cat = next((c for c in self._cats if c.nombre == cat_name), None)
            if cat is None:
                raise ValueError("Categoría inválida.")

            try:
                precio = float(precio_s)
                stock  = int(stock_s)
            except ValueError:
                raise ValueError("Precio y stock deben ser números válidos.")

            if self._pid is None:
                svc.crear(codigo, nombre, cat.id, precio, stock)
            else:
                svc.editar(self._pid, codigo, nombre, cat.id, precio, stock)

            self._parent.cargar()
            self.destroy()
        except IntegrityError:
            self._lbl_err.config(text="Ya existe un producto con ese código.")
        except Exception as e:
            self._lbl_err.config(text=str(e))
