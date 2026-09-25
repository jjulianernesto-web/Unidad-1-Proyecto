"""
ui/main_window.py – Ventana principal con menú, Notebook y barra de estado.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import BG, SURFACE, CARD, ACCENT, FG, FG2, FONT_BODY, FONT_SMALL, apply_theme
from models import Usuario


class MainWindow(tk.Tk):
    def __init__(self, usuario: Usuario):
        super().__init__()
        self._usuario = usuario
        self.title("Mini POS – Punto de Venta")
        self.geometry("1050x680")
        self.minsize(880, 560)
        apply_theme(self)
        self._build_menu()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.eval("tk::PlaceWindow . center")

    # ── Menú ─────────────────────────────────────────────────────────────
    def _build_menu(self):
        menu = tk.Menu(self, bg=SURFACE, fg=FG, activebackground=ACCENT,
                       activeforeground="#fff", relief="flat", borderwidth=0)
        self.config(menu=menu)

        m_catalogo = tk.Menu(menu, tearoff=0, bg=SURFACE, fg=FG,
                             activebackground=ACCENT, activeforeground="#fff")
        m_catalogo.add_command(label="📦 Productos",   command=lambda: self._go_to(1))
        m_catalogo.add_command(label="📂 Categorías",  command=lambda: self._go_to(2))
        menu.add_cascade(label="Catálogo", menu=m_catalogo)

        m_ventas = tk.Menu(menu, tearoff=0, bg=SURFACE, fg=FG,
                           activebackground=ACCENT, activeforeground="#fff")
        m_ventas.add_command(label="🛒 Nueva Venta",   command=lambda: self._go_to(3))
        m_ventas.add_command(label="📜 Historial",     command=lambda: self._go_to(3))
        menu.add_cascade(label="Ventas", menu=m_ventas)

        m_rep = tk.Menu(menu, tearoff=0, bg=SURFACE, fg=FG,
                        activebackground=ACCENT, activeforeground="#fff")
        m_rep.add_command(label="📊 Reportes", command=lambda: self._go_to(4))
        menu.add_cascade(label="Reportes", menu=m_rep)

        if self._usuario.rol == "administrador":
            m_adm = tk.Menu(menu, tearoff=0, bg=SURFACE, fg=FG,
                            activebackground=ACCENT, activeforeground="#fff")
            m_adm.add_command(label="👥 Usuarios", command=lambda: self._go_to(5))
            menu.add_cascade(label="Administración", menu=m_adm)

        menu.add_command(label="🚪 Cerrar sesión", command=self._logout)

    # ── UI principal ─────────────────────────────────────────────────────
    def _build_ui(self):
        # Barra superior
        topbar = tk.Frame(self, bg=SURFACE, height=46)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="🏪  Mini POS", font=("Segoe UI", 13, "bold"),
                 bg=SURFACE, fg=ACCENT).pack(side="left", padx=16, pady=8)
        tk.Label(topbar, text=f"  |  {self._usuario.nombre_completo}  •  {self._usuario.rol.capitalize()}",
                 font=FONT_SMALL, bg=SURFACE, fg=FG2).pack(side="left", pady=8)

        # Notebook principal
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True, padx=8, pady=8)

        # Importar frames aquí para evitar importaciones circulares
        from ui.producto_frame  import ProductoFrame
        from ui.categoria_frame import CategoriaFrame
        from ui.venta_frame     import VentaFrame
        from ui.reporte_frame   import ReporteFrame

        self._frames: dict[int, ttk.Frame] = {}

        tab_prod = ttk.Frame(self._nb)
        self._nb.add(tab_prod, text="  📦 Productos  ")
        self._frames[1] = ProductoFrame(tab_prod, self._usuario)
        self._frames[1].pack(fill="both", expand=True, padx=12, pady=8)

        tab_cat = ttk.Frame(self._nb)
        self._nb.add(tab_cat, text="  📂 Categorías  ")
        self._frames[2] = CategoriaFrame(tab_cat, self._usuario)
        self._frames[2].pack(fill="both", expand=True, padx=12, pady=8)

        tab_vta = ttk.Frame(self._nb)
        self._nb.add(tab_vta, text="  🛒 Ventas  ")
        self._frames[3] = VentaFrame(tab_vta, self._usuario)
        self._frames[3].pack(fill="both", expand=True, padx=12, pady=8)

        tab_rep = ttk.Frame(self._nb)
        self._nb.add(tab_rep, text="  📊 Reportes  ")
        self._frames[4] = ReporteFrame(tab_rep, self._usuario)
        self._frames[4].pack(fill="both", expand=True, padx=12, pady=8)

        if self._usuario.rol == "administrador":
            from ui.usuario_frame import UsuarioFrame
            tab_usr = ttk.Frame(self._nb)
            self._nb.add(tab_usr, text="  👥 Usuarios  ")
            self._frames[5] = UsuarioFrame(tab_usr, self._usuario)
            self._frames[5].pack(fill="both", expand=True, padx=12, pady=8)

        # Barra de estado
        status = tk.Frame(self, bg=CARD, height=22)
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)
        tk.Label(status, text="Mini POS  •  Opción 2 – Inventario / Punto de Venta  •  Tópicos Avanzados de Programación",
                 font=("Segoe UI", 8), bg=CARD, fg=FG2).pack(side="left", padx=10)

    def _go_to(self, tab_index: int):
        tabs = list(self._frames.keys())
        if tab_index in tabs:
            self._nb.select(tabs.index(tab_index))

    def _logout(self):
        if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar sesión?", parent=self):
            self.destroy()

    def _on_close(self):
        if messagebox.askyesno("Salir", "¿Deseas salir de Mini POS?", parent=self):
            self.destroy()
