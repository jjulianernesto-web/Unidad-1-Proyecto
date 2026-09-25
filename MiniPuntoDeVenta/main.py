"""
main.py – Punto de entrada de Mini POS.
Opción 2: Inventario / Mini Punto de Venta
Tópicos Avanzados de Programación – Unidad 1
"""
import sys
import os

# Añadir la raíz del proyecto al path para imports absolutos
sys.path.insert(0, os.path.dirname(__file__))

from db.database import init_db
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def main():
    # 1. Inicializar base de datos (crea tablas + semilla si no existen)
    init_db()

    # 2. Mostrar pantalla de login
    login = LoginWindow()
    login.mainloop()

    # 3. Si el usuario inició sesión, abrir ventana principal
    usuario = login.usuario
    if usuario:
        app = MainWindow(usuario)
        app.mainloop()


if __name__ == "__main__":
    main()
