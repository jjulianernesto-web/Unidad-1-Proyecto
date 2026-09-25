"""
ui/theme.py – Paleta de colores y configuración del tema ttk.
"""
import tkinter as tk
from tkinter import ttk

# ── Paleta ──────────────────────────────────────────────────────────────────
BG       = "#0f1117"   # fondo principal oscuro
SURFACE  = "#1a1d27"   # tarjetas / frames
CARD     = "#22263a"   # headers de tarjeta
ACCENT   = "#7c5cfc"   # violeta
ACCENT2  = "#5a9cf5"   # azul claro
SUCCESS  = "#2ecc71"
WARNING  = "#f39c12"
DANGER   = "#e74c3c"
FG       = "#e8eaf6"   # texto principal
FG2      = "#9099b7"   # texto secundario

FONT_TITLE  = ("Segoe UI", 14, "bold")
FONT_HEADER = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)

BTN_PAD = {"padx": 12, "pady": 6}


def apply_theme(root: tk.Tk | tk.Toplevel) -> ttk.Style:
    root.configure(bg=BG)
    style = ttk.Style(root)
    style.theme_use("clam")

    # Frame / LabelFrame
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=SURFACE)
    style.configure("TLabelframe", background=SURFACE, foreground=FG,
                    bordercolor=CARD, relief="flat")
    style.configure("TLabelframe.Label", background=SURFACE, foreground=ACCENT,
                    font=FONT_HEADER)

    # Labels
    style.configure("TLabel", background=BG, foreground=FG, font=FONT_BODY)
    style.configure("Card.TLabel", background=SURFACE, foreground=FG, font=FONT_BODY)
    style.configure("Muted.TLabel", background=BG, foreground=FG2, font=FONT_SMALL)
    style.configure("Title.TLabel", background=BG, foreground=FG, font=FONT_TITLE)
    style.configure("Accent.TLabel", background=BG, foreground=ACCENT, font=FONT_HEADER)

    # Entry
    style.configure("TEntry", fieldbackground=CARD, foreground=FG,
                    insertcolor=FG, bordercolor=ACCENT, relief="flat")
    style.map("TEntry", bordercolor=[("focus", ACCENT2)])

    # Buttons
    style.configure("TButton", background=ACCENT, foreground="#ffffff",
                    font=FONT_BODY, relief="flat", borderwidth=0)
    style.map("TButton",
              background=[("active", ACCENT2), ("disabled", CARD)],
              foreground=[("disabled", FG2)])

    style.configure("Danger.TButton", background=DANGER, foreground="#fff",
                    font=FONT_BODY, relief="flat", borderwidth=0)
    style.map("Danger.TButton", background=[("active", "#c0392b")])

    style.configure("Success.TButton", background=SUCCESS, foreground="#fff",
                    font=FONT_BODY, relief="flat", borderwidth=0)
    style.map("Success.TButton", background=[("active", "#27ae60")])

    style.configure("Warn.TButton", background=WARNING, foreground="#fff",
                    font=FONT_BODY, relief="flat", borderwidth=0)
    style.map("Warn.TButton", background=[("active", "#e67e22")])

    # Combobox
    style.configure("TCombobox", fieldbackground=CARD, foreground=FG,
                    background=CARD, arrowcolor=ACCENT)
    style.map("TCombobox", fieldbackground=[("readonly", CARD)])

    # Treeview
    style.configure("Treeview", background=SURFACE, foreground=FG,
                    fieldbackground=SURFACE, rowheight=26, borderwidth=0,
                    font=FONT_BODY)
    style.configure("Treeview.Heading", background=CARD, foreground=ACCENT,
                    font=FONT_HEADER, relief="flat")
    style.map("Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", "#fff")])

    # Notebook
    style.configure("TNotebook", background=BG, tabmargins=[2, 4, 0, 0])
    style.configure("TNotebook.Tab", background=CARD, foreground=FG2,
                    font=FONT_BODY, padding=[12, 6])
    style.map("TNotebook.Tab",
              background=[("selected", SURFACE)],
              foreground=[("selected", ACCENT)])

    # Separator
    style.configure("TSeparator", background=CARD)

    # Scrollbar
    style.configure("TScrollbar", background=CARD, troughcolor=SURFACE,
                    arrowcolor=FG2, bordercolor=SURFACE, relief="flat")

    return style
