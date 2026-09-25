"""
ui/login_window.py – Pantalla de inicio de sesión.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import (BG, SURFACE, CARD, ACCENT, ACCENT2, FG, FG2,
                      FONT_TITLE, FONT_HEADER, FONT_BODY, FONT_SMALL, apply_theme)
from services.auth_service import login, AuthError
from models import Usuario


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mini POS – Acceso")
        self.resizable(False, False)
        self.geometry("420x500")
        self._usuario: Usuario | None = None
        apply_theme(self)
        self._build_ui()
        self.eval("tk::PlaceWindow . center")

    # ── UI ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Fondo con gradiente simulado
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        # Tarjeta central
        card = tk.Frame(outer, bg=SURFACE, bd=0, highlightthickness=1,
                        highlightbackground=ACCENT)
        card.place(relx=0.5, rely=0.5, anchor="center", width=320, height=380)

        # Logo / título
        tk.Label(card, text="🏪", font=("Segoe UI Emoji", 36), bg=SURFACE, fg=ACCENT).pack(pady=(32, 4))
        tk.Label(card, text="Mini POS", font=FONT_TITLE, bg=SURFACE, fg=FG).pack()
        tk.Label(card, text="Punto de Venta", font=FONT_SMALL, bg=SURFACE, fg=FG2).pack(pady=(0, 24))

        sep = ttk.Separator(card)
        sep.pack(fill="x", padx=24, pady=(0, 20))

        # Usuario
        ttk.Label(card, text="Usuario", style="Card.TLabel").pack(anchor="w", padx=30)
        self._var_user = tk.StringVar()
        ent_user = ttk.Entry(card, textvariable=self._var_user, font=FONT_BODY)
        ent_user.pack(fill="x", padx=30, pady=(2, 12), ipady=6)

        # Contraseña
        ttk.Label(card, text="Contraseña", style="Card.TLabel").pack(anchor="w", padx=30)
        self._var_pw = tk.StringVar()
        ent_pw = ttk.Entry(card, textvariable=self._var_pw, show="•", font=FONT_BODY)
        ent_pw.pack(fill="x", padx=30, pady=(2, 20), ipady=6)

        # Error
        self._lbl_err = tk.Label(card, text="", bg=SURFACE, fg="#e74c3c",
                                 font=FONT_SMALL, wraplength=260)
        self._lbl_err.pack(pady=(0, 8))

        # Botón
        btn = ttk.Button(card, text="Iniciar sesión", command=self._do_login)
        btn.pack(fill="x", padx=30, ipady=6)

        # Enter key
        self.bind("<Return>", lambda _e: self._do_login())
        ent_user.focus()

    # ── Lógica ───────────────────────────────────────────────────────────
    def _do_login(self):
        self._lbl_err.config(text="")
        try:
            self._usuario = login(self._var_user.get(), self._var_pw.get())
            self.destroy()
        except AuthError as e:
            self._lbl_err.config(text=str(e))
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e), parent=self)

    @property
    def usuario(self) -> Usuario | None:
        return self._usuario
