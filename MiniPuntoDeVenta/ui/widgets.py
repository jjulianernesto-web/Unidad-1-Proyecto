"""
ui/widgets.py – Widgets reutilizables: Treeview con scrollbar, búsqueda, etc.
"""
import tkinter as tk
from tkinter import ttk
from ui.theme import BG, SURFACE, CARD, ACCENT, FG2, FG, FONT_BODY, FONT_SMALL


def make_tree(parent, columns: list[tuple[str, str, int]], height: int = 14) -> ttk.Treeview:
    """
    columns: [(col_id, heading, width), ...]
    Devuelve el Treeview ya empaquetado con scrollbar.
    """
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True, padx=0, pady=0)

    scroll_y = ttk.Scrollbar(frame, orient="vertical")
    scroll_y.pack(side="right", fill="y")

    col_ids = [c[0] for c in columns]
    tree = ttk.Treeview(frame, columns=col_ids, show="headings",
                        height=height, yscrollcommand=scroll_y.set)
    tree.pack(fill="both", expand=True)
    scroll_y.config(command=tree.yview)

    for col_id, heading, width in columns:
        tree.heading(col_id, text=heading)
        tree.column(col_id, width=width, anchor="w", minwidth=40)

    # Filas alternas
    tree.tag_configure("par", background=SURFACE)
    tree.tag_configure("impar", background=CARD)
    tree.tag_configure("alerta", background="#3a1e1e", foreground="#ff6b6b")
    tree.tag_configure("ok", background="#1a2e1a", foreground="#6bff8a")

    return tree


def reload_tree(tree: ttk.Treeview, rows: list[tuple], tags: list[str] | None = None):
    """Limpia y vuelve a cargar filas en el Treeview."""
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        tag = tags[i] if tags else ("par" if i % 2 == 0 else "impar")
        tree.insert("", "end", values=row, tags=(tag,))


def search_bar(parent, command) -> tk.StringVar:
    """Barra de búsqueda con icono y Entry. Devuelve la StringVar."""
    frame = ttk.Frame(parent)
    frame.pack(fill="x", pady=(0, 8))
    tk.Label(frame, text="🔍", font=("Segoe UI Emoji", 11), bg=BG, fg=FG2).pack(side="left", padx=(0, 4))
    var = tk.StringVar()
    ent = ttk.Entry(frame, textvariable=var, font=FONT_BODY, width=30)
    ent.pack(side="left", ipady=4)
    var.trace_add("write", lambda *_: command())
    tk.Label(frame, text="Buscar…", bg=BG, fg=FG2, font=FONT_SMALL).pack(side="left", padx=6)
    return var


def action_bar(parent, actions: list[tuple[str, str, callable]]) -> dict[str, ttk.Button]:
    """
    actions: [(text, style, callback), ...]
    Devuelve dict {text: button}.
    """
    frame = ttk.Frame(parent)
    frame.pack(fill="x", pady=(8, 0))
    buttons = {}
    for text, style, cb in actions:
        btn = ttk.Button(frame, text=text, style=style, command=cb)
        btn.pack(side="left", padx=(0, 6), ipady=4)
        buttons[text] = btn
    return buttons


def labeled_entry(parent, label: str, var: tk.Variable, row: int, col: int = 0,
                  show: str = "", width: int = 28) -> ttk.Entry:
    ttk.Label(parent, text=label).grid(row=row, column=col, sticky="w", pady=4, padx=(0, 8))
    ent = ttk.Entry(parent, textvariable=var, show=show, font=FONT_BODY, width=width)
    ent.grid(row=row, column=col + 1, sticky="ew", pady=4)
    return ent


def labeled_combo(parent, label: str, var: tk.Variable, values: list,
                  row: int, col: int = 0, width: int = 26) -> ttk.Combobox:
    ttk.Label(parent, text=label).grid(row=row, column=col, sticky="w", pady=4, padx=(0, 8))
    combo = ttk.Combobox(parent, textvariable=var, values=values,
                         state="readonly", font=FONT_BODY, width=width)
    combo.grid(row=row, column=col + 1, sticky="ew", pady=4)
    return combo
