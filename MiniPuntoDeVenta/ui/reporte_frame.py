"""
ui/reporte_frame.py – Reporte: stock bajo y productos más vendidos.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from ui.theme import BG, SURFACE, ACCENT, FG2, FONT_SMALL
from ui import widgets as W
import services.producto_service as svc


class ReporteFrame(ttk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.usuario = usuario
        self._build()
        self.cargar()

    def _build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self._tab_bajo   = ttk.Frame(nb)
        self._tab_top    = ttk.Frame(nb)
        nb.add(self._tab_bajo, text="  ⚠️  Stock Bajo  ")
        nb.add(self._tab_top,  text="  🏆  Más Vendidos  ")

        self._build_stock_bajo(self._tab_bajo)
        self._build_mas_vendidos(self._tab_top)

    # ── Stock bajo ───────────────────────────────────────────────────────
    def _build_stock_bajo(self, parent):
        hdr = ttk.Frame(parent)
        hdr.pack(fill="x", pady=(6, 0))
        ttk.Label(hdr, text="⚠️  Productos con Stock Bajo", style="Accent.TLabel").pack(side="left")

        umbral_f = ttk.Frame(parent)
        umbral_f.pack(fill="x", pady=4)
        ttk.Label(umbral_f, text="Umbral (≤):").pack(side="left")
        self._var_umbral = tk.StringVar(value="5")
        ttk.Entry(umbral_f, textvariable=self._var_umbral, width=5).pack(side="left", padx=4, ipady=3)
        ttk.Button(umbral_f, text="Actualizar", command=self._cargar_bajo).pack(side="left", padx=6, ipady=3)
        ttk.Button(umbral_f, text="📥 Exportar CSV", style="Success.TButton",
                   command=self._exportar_bajo).pack(side="left", padx=4, ipady=3)

        cols = [("codigo", "Código", 80), ("nombre", "Nombre", 200),
                ("categoria", "Categoría", 120), ("precio", "Precio", 75),
                ("stock", "Stock", 60)]
        self._tree_bajo = W.make_tree(parent, cols, height=16)

    def _cargar_bajo(self):
        try:
            umbral = int(self._var_umbral.get())
        except ValueError:
            umbral = 5
        prods = svc.reporte_stock_bajo(umbral)
        rows  = [(p.codigo, p.nombre, p.categoria_nombre, f"${p.precio:.2f}", p.stock)
                 for p in prods]
        tags  = [("alerta" if p.stock == 0 else "impar") for p in prods]
        W.reload_tree(self._tree_bajo, rows, tags)

    def _exportar_bajo(self):
        try:
            umbral = int(self._var_umbral.get())
        except ValueError:
            umbral = 5
        prods = svc.reporte_stock_bajo(umbral)
        path  = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            initialfile="stock_bajo.csv", parent=self)
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Código", "Nombre", "Categoría", "Precio", "Stock"])
            for p in prods:
                w.writerow([p.codigo, p.nombre, p.categoria_nombre, p.precio, p.stock])
        messagebox.showinfo("Exportado", f"Archivo guardado en:\n{path}", parent=self)

    # ── Más vendidos ─────────────────────────────────────────────────────
    def _build_mas_vendidos(self, parent):
        ttk.Label(parent, text="🏆  Productos Más Vendidos", style="Accent.TLabel").pack(
            anchor="w", pady=(6, 6))
        ttk.Button(parent, text="📥 Exportar CSV", style="Success.TButton",
                   command=self._exportar_top).pack(anchor="w", pady=(0, 6), ipady=3)

        cols = [("codigo", "Código", 80), ("nombre", "Nombre", 200),
                ("cat", "Categoría", 120), ("vendido", "Total Vendido", 100),
                ("ingresos", "Ingresos", 90)]
        self._tree_top = W.make_tree(parent, cols, height=16)

    def _cargar_top(self):
        datos = svc.reporte_mas_vendidos()
        rows  = [(d["codigo"], d["nombre"], d["categoria"],
                  d["total_vendido"], f"${d['ingresos']:.2f}")
                 for d in datos]
        W.reload_tree(self._tree_top, rows)

    def _exportar_top(self):
        datos = svc.reporte_mas_vendidos()
        path  = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            initialfile="mas_vendidos.csv", parent=self)
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Código", "Nombre", "Categoría", "Total Vendido", "Ingresos"])
            for d in datos:
                w.writerow([d["codigo"], d["nombre"], d["categoria"],
                            d["total_vendido"], d["ingresos"]])
        messagebox.showinfo("Exportado", f"Archivo guardado en:\n{path}", parent=self)

    def cargar(self):
        self._cargar_bajo()
        self._cargar_top()
