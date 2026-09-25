"""
ui/categoria_frame.py – CRUD de categorías (Treeview + formulario Toplevel).
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import BG, SURFACE, CARD, ACCENT, FG, FONT_HEADER
from ui import widgets as W
import services.categoria_service as svc
from sqlite3 import IntegrityError


class CategoriaFrame(ttk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.usuario = usuario
        self._build()
        self.cargar()

    def _build(self):
        # Encabezado
        hdr = ttk.Frame(self)
        hdr.pack(fill="x", pady=(0, 8))
        ttk.Label(hdr, text="📂  Categorías", style="Accent.TLabel").pack(side="left")

        # Barra de búsqueda
        self._var_buscar = W.search_bar(self, self.cargar)

        # Treeview
        cols = [("id", "ID", 40), ("nombre", "Nombre", 220), ("estado", "Estado", 80)]
        self._tree = W.make_tree(self, cols, height=16)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # Botones
        is_admin = self.usuario.rol == "administrador"
        acciones = [("➕ Nueva", "TButton", self._nueva)]
        if is_admin:
            acciones += [
                ("✏️ Editar", "TButton", self._editar),
                ("🚫 Desactivar", "Warn.TButton", self._desactivar),
                ("✅ Activar", "Success.TButton", self._activar),
            ]
        self._btns = W.action_bar(self, acciones)
        self._selected_id: int | None = None

    def cargar(self):
        buscar = self._var_buscar.get().lower()
        cats = svc.listar()
        filtradas = [c for c in cats if buscar in c.nombre.lower()] if buscar else cats
        rows = [(c.id, c.nombre, "Activa" if c.activo else "Inactiva") for c in filtradas]
        tags = [("ok" if c.activo else "alerta") for c in filtradas]
        W.reload_tree(self._tree, rows, tags)

    def _on_select(self, _e=None):
        sel = self._tree.selection()
        if sel:
            self._selected_id = int(self._tree.item(sel[0])["values"][0])

    def _get_selected_id(self) -> int | None:
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona una categoría.", parent=self)
            return None
        return int(self._tree.item(sel[0])["values"][0])

    def _nueva(self):
        _FormCategoria(self, None)

    def _editar(self):
        cid = self._get_selected_id()
        if cid:
            _FormCategoria(self, cid)

    def _desactivar(self):
        cid = self._get_selected_id()
        if not cid:
            return
        if not messagebox.askyesno("Confirmar", "¿Desactivar esta categoría?", parent=self):
            return
        try:
            svc.desactivar(cid)
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _activar(self):
        cid = self._get_selected_id()
        if not cid:
            return
        try:
            svc.activar(cid)
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)


class _FormCategoria(tk.Toplevel):
    def __init__(self, parent: CategoriaFrame, cid: int | None):
        super().__init__(parent)
        self._parent = parent
        self._cid = cid
        self.title("Nueva categoría" if cid is None else "Editar categoría")
        self.resizable(False, False)
        self.configure(bg=SURFACE)
        self.grab_set()
        self._build()
        if cid:
            cats = svc.listar()
            cat = next((c for c in cats if c.id == cid), None)
            if cat:
                self._var_nombre.set(cat.nombre)
        self.eval(f"tk::PlaceWindow {self} center")

    def _build(self):
        frame = tk.Frame(self, bg=SURFACE, padx=24, pady=20)
        frame.pack()
        ttk.Label(frame, text="Nombre de la categoría", style="Card.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 4))
        self._var_nombre = tk.StringVar()
        ent = ttk.Entry(frame, textvariable=self._var_nombre, font=("Segoe UI", 10), width=30)
        ent.grid(row=1, column=0, ipady=6, pady=(0, 16))
        ent.focus()

        self._lbl_err = tk.Label(frame, text="", bg=SURFACE, fg="#e74c3c",
                                 font=("Segoe UI", 9), wraplength=220)
        self._lbl_err.grid(row=2, column=0, pady=(0, 8))

        ttk.Button(frame, text="💾 Guardar", command=self._guardar).grid(
            row=3, column=0, ipadx=10, ipady=6, sticky="ew")

    def _guardar(self):
        self._lbl_err.config(text="")
        try:
            nombre = self._var_nombre.get()
            if self._cid is None:
                svc.crear(nombre)
            else:
                svc.editar(self._cid, nombre)
            self._parent.cargar()
            self.destroy()
        except IntegrityError:
            self._lbl_err.config(text="Ya existe una categoría con ese nombre.")
        except Exception as e:
            self._lbl_err.config(text=str(e))
