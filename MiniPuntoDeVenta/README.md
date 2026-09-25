# Mini POS – Inventario / Punto de Venta

> **Opción 2 · Tópicos Avanzados de Programación – Unidad 1**  
> Tecnología: Python 3.10+ · Tkinter + SQLite3 · sin dependencias externas

---

## Descripción

**Mini POS** es un sistema de punto de venta ligero para locales pequeños (papelería, cafetería, tienda escolar). Permite controlar el catálogo de productos por categoría, registrar ventas con detalle de ítems, descontar stock automáticamente y generar reportes de stock bajo y productos más vendidos.

---

## Requisitos

| Requisito | Versión mínima |
|-----------|---------------|
| Python    | 3.10+         |
| Tkinter   | incluido en Python estándar |
| SQLite3   | incluido en Python estándar |

> **Sin dependencias externas.** No se requiere `pip install`.

---

## Instalación y ejecución

```bash
# 1. Clonar el repositorio (o descomprimir el ZIP)
git clone https://github.com/<usuario>/mini-pos.git
cd mini-pos/mini_pos

# 2. Ejecutar directamente
python main.py
```

Al primer arranque se crea automáticamente el archivo `mini_pos.db` con tablas y datos de prueba.

---

## Usuarios de prueba

| Usuario    | Contraseña | Rol            |
|------------|------------|----------------|
| `admin`    | `admin123` | administrador  |
| `operador1`| `op123`    | operador       |

El **administrador** puede gestionar usuarios, categorías, productos y ver reportes.  
El **operador** puede gestionar productos, registrar ventas y ver reportes (sin gestión de usuarios ni acceso a desactivar registros críticos).

---

## Modelo de datos

```
usuarios_sistema  ──────────────────────────────┐
  id, username(UNIQUE), password_hash,           │
  nombre_completo, rol, activo                   │
                                                 │
categorias                                       │
  id, nombre(UNIQUE), activo                     │
      │                                          │
      ▼                                          │
productos                                        │
  id, codigo(UNIQUE), nombre,                    │
  categoria_id FK→categorias,                    │
  precio REAL>0, stock INTEGER≥0, activo         │
      │                                          │
      ▼                          ┌───────────────┘
ventas ◄──────────────────────── │
  id, fecha(ISO), usuario_id FK──┘, total
      │
      ▼
detalle_venta
  id, venta_id FK→ventas,
  producto_id FK→productos,
  cantidad, precio_unitario, subtotal
```

---

## Funcionalidades implementadas

### CRUD
| Módulo      | Alta | Listado | Edición | Desactivar/Activar |
|-------------|------|---------|---------|-------------------|
| Categorías  | ✅   | ✅      | ✅      | ✅                |
| Productos   | ✅   | ✅      | ✅      | ✅                |
| Usuarios    | ✅   | ✅      | —       | ✅                |

### Movimiento de negocio
- **Nueva Venta**: carrito interactivo con búsqueda de productos, cantidad configurable.
- Cada venta tiene uno o más ítems en `detalle_venta`.
- El `precio_unitario` se copia del catálogo al momento de la venta (precio histórico).
- El stock se descuenta atómicamente junto con el INSERT del detalle.
- Las ventas **no se borran**: quedan registradas permanentemente.

### Reglas de negocio
- ❌ No vender si `cantidad > stock` disponible.
- ❌ No vender producto inactivo.
- ❌ No desactivar categoría con productos activos.
- ❌ No desactivar usuario activo que sea el mismo que sesionó.
- 🔒 Contraseñas con hash SHA-256 (nunca en texto plano).
- 🔒 Confirmación con `messagebox` antes de desactivar registros.

### Reporte
- **Stock bajo**: productos activos con stock ≤ umbral configurable (defecto 5).
- **Más vendidos**: ranking por total de unidades vendidas con ingresos.
- **Exportar CSV**: ambos reportes exportables.

### JOIN obligatorio
```sql
-- Historial de ventas con nombre de usuario
SELECT v.*, u.nombre_completo AS usr_nombre
FROM ventas v
JOIN usuarios_sistema u ON u.id = v.usuario_id

-- Detalle de venta con nombre del producto
SELECT dv.*, p.nombre AS prod_nombre
FROM detalle_venta dv
JOIN productos p ON p.id = dv.producto_id
WHERE dv.venta_id = ?
```

---

## Estructura del proyecto

```
mini_pos/
├── main.py                    # Punto de entrada
├── requirements.txt
├── mini_pos.db                # Creado automáticamente al primer arranque
│
├── db/
│   └── database.py            # Conexión, PRAGMA FK, CREATE TABLE, semilla
│
├── models/
│   └── __init__.py            # Dataclasses: Usuario, Categoria, Producto, Venta, DetalleVenta
│
├── repositories/
│   ├── usuario_repo.py        # SQL de usuarios_sistema
│   ├── categoria_repo.py      # SQL de categorias
│   ├── producto_repo.py       # SQL de productos (con JOIN a categorias)
│   └── venta_repo.py          # SQL de ventas + detalle_venta (JOIN obligatorio)
│
├── services/
│   ├── auth_service.py        # Reglas de autenticación y gestión de usuarios
│   ├── categoria_service.py   # Reglas de categorías (integridad referencial)
│   ├── producto_service.py    # Validación de precio/stock, reportes
│   └── venta_service.py       # Proceso de venta: validación + precio histórico
│
└── ui/
    ├── theme.py               # Paleta oscura + estilos ttk
    ├── widgets.py             # Treeview, search_bar, action_bar reutilizables
    ├── login_window.py        # LoginWindow (tk.Tk)
    ├── main_window.py         # MainWindow con Notebook y menú
    ├── categoria_frame.py     # CRUD de categorías
    ├── producto_frame.py      # CRUD de productos
    ├── venta_frame.py         # Nueva venta + historial
    ├── reporte_frame.py       # Stock bajo + más vendidos + CSV
    └── usuario_frame.py       # Gestión de usuarios (solo admin)
```

---

## Arquitectura (separación de capas)

```
[ UI / Botones ]  →  [ Services / Reglas de negocio ]  →  [ Repositories / SQL ]  →  [ SQLite DB ]
```

- **La UI no contiene SQL**: los botones llaman servicios.
- **Los servicios no conocen Tkinter**: las reglas de negocio funcionarían igual en consola.
- **Los repositorios solo hacen SQL** y mapean filas a objetos de dominio.

---

## Extras implementados

| Extra | Estado |
|-------|--------|
| Exportar CSV (stock bajo y más vendidos) | ✅ |
| Tema oscuro (paleta violeta-azul) | ✅ |

---

## Datos de prueba incluidos

- **10 productos** en 5 categorías (2 con stock bajo, 1 inactivo con stock 0).
- **3 ventas**: una pasada (2026-09-20), una de hoy y una intermedia.
- **1 categoría** de "Útiles escolares" con productos activos (para probar regla de integridad).

---

## Notas y limitaciones conocidas

- El `.db` se crea en la misma carpeta que `main.py` (`mini_pos/mini_pos.db`).
- No se implementó edición de contraseña de usuario (fuera del alcance pedido).
- Los emojis en los botones requieren Windows 10+ o macOS con fuentes de emoji instaladas.
