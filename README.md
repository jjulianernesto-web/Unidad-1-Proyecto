# Mini POS – Sistema de Punto de Venta 🛒

Un sistema de punto de venta ligero y rápido, desarrollado con **Python**, **Tkinter** y **SQLite3**. Diseñado especialmente para negocios pequeños como papelerías o cafeterías. No requiere instalaciones complejas ni dependencias externas.

## ✨ Características Principales

*   **Punto de Venta**: Registro ágil de ventas, carrito interactivo y descuento automático de stock.
*   **Gestión de Inventario**: Control completo (CRUD) de categorías y productos.
*   **Reportes**: Detección de stock bajo y ranking de los productos más vendidos (exportables a CSV).
*   **Usuarios y Roles**: Acceso seguro (contraseñas con hash SHA-256) para perfiles de `Administrador` y `Operador`.
*   **Arquitectura Limpia**: Separación de capas (UI, Lógica de Negocio y Base de Datos) con un diseño visual moderno (modo oscuro).

## 🚀 Instalación y Ejecución

Solo necesitas tener **Python 3.10 o superior** instalado. No es necesario usar `pip install`.

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/mini-pos.git
   cd mini-pos/mini_pos
   ```
2. Ejecuta el archivo principal:
   ```bash
   python main.py
   ```
*(Al iniciar por primera vez, se generará automáticamente la base de datos `mini_pos.db` con información de prueba).*

## 🔐 Usuarios de Prueba Incluidos

Puedes probar el sistema con las siguientes cuentas:

| Usuario | Contraseña | Rol | Permisos |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | Administrador | Acceso total (usuarios, reportes, inventario completo). |
| `operador1` | `op123` | Operador | Ventas y gestión básica de productos. |
