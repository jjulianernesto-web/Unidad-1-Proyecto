"""
ui/usuario_frame.py – Gestión de usuarios (solo administrador).
"""
import tkinter as tk
from tkinter import ttk, messagebox
from sqlite3 import IntegrityError
from ui.theme import SURFACE
from ui import widgets as W
import services.auth_service as svc


class UsuarioFrame(ttk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.usuario = usuario
        self._build()
        self.cargar()

    def _build(self):
        ttk.Label(self, text="👥  Usuarios del Sistema", style="Accent.TLabel").pack(
            anchor="w", pady=(0, 8))
        self._var_buscar = W.search_bar(self, self.cargar)

        cols = [("id", "ID", 35), ("user", "Usuario", 110),
                ("nombre", "Nombre", 180), ("rol", "Rol", 100), ("estado", "Estado", 70)]
        self._tree = W.make_tree(self, cols, height=14)

        acciones = [
            ("➕ Nuevo", "TButton", self._nuevo),
            ("🚫 Desactivar", "Warn.TButton", self._desactivar),
            ("✅ Activar", "Success.TButton", self._activar),
        ]
        W.action_bar(self, acciones)

    def cargar(self):
        buscar = self._var_buscar.get().lower()
        users  = svc.listar_usuarios()
        if buscar:
            users = [u for u in users if buscar in u.username.lower()
                     or buscar in u.nombre_completo.lower()]
        rows = [(u.id, u.username, u.nombre_completo, u.rol,
                 "Activo" if u.activo else "Inactivo") for u in users]
        tags = [("ok" if u.activo else "alerta") for u in users]
        W.reload_tree(self._tree, rows, tags)

    def _get_selected_id(self) -> int | None:
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona un usuario.", parent=self)
            return None
        return int(self._tree.item(sel[0])["values"][0])

    def _nuevo(self):
        _FormUsuario(self)

    def _desactivar(self):
        uid = self._get_selected_id()
        if not uid:
            return
        if uid == self.usuario.id:
            messagebox.showerror("Error", "No puedes desactivarte a ti mismo.", parent=self)
            return
        if not messagebox.askyesno("Confirmar", "¿Desactivar este usuario?", parent=self):
            return
        svc.desactivar_usuario(uid)
        self.cargar()

    def _activar(self):
        uid = self._get_selected_id()
        if not uid:
            return
        svc.activar_usuario(uid)
        self.cargar()


class _FormUsuario(tk.Toplevel):
    def __init__(self, parent: UsuarioFrame):
        super().__init__(parent)
        self._parent = parent
        self.title("Nuevo usuario")
        self.resizable(False, False)
        self.configure(bg=SURFACE)
        self.grab_set()
        self._build()
        self.eval(f"tk::PlaceWindow {self} center")

    def _build(self):
        frame = tk.Frame(self, bg=SURFACE, padx=28, pady=24)
        frame.pack()
        frame.columnconfigure(1, weight=1)

        self._var_user   = tk.StringVar()
        self._var_pw     = tk.StringVar()
        self._var_nombre = tk.StringVar()
        self._var_rol    = tk.StringVar(value="operador")

        W.labeled_entry(frame, "Usuario *", self._var_user, 0)
        W.labeled_entry(frame, "Contraseña *", self._var_pw, 1, show="•")
        W.labeled_entry(frame, "Nombre completo *", self._var_nombre, 2)
        W.labeled_combo(frame, "Rol *", self._var_rol,
                        ["administrador", "operador"], 3)

        self._lbl_err = tk.Label(frame, text="", bg=SURFACE, fg="#e74c3c",
                                 font=("Segoe UI", 9), wraplength=260)
        self._lbl_err.grid(row=4, column=0, columnspan=2, pady=(8, 4))

        ttk.Button(frame, text="💾 Guardar", command=self._guardar).grid(
            row=5, column=0, columnspan=2, ipadx=10, ipady=6, sticky="ew")

    def _guardar(self):
        self._lbl_err.config(text="")
        try:
            svc.crear_usuario(
                self._var_user.get(), self._var_pw.get(),
                self._var_nombre.get(), self._var_rol.get()
            )
            self._parent.cargar()
            self.destroy()
        except IntegrityError:
            self._lbl_err.config(text="Ese nombre de usuario ya existe.")
        except Exception as e:
            self._lbl_err.config(text=str(e))
