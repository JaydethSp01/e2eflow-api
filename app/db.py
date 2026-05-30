import os
import threading
from typing import Optional, Any, List, Dict

try:
    import psycopg
    from psycopg.rows import dict_row
    PSYCOPG_OK = True
except Exception:
    PSYCOPG_OK = False

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

_memory: Dict[str, List[Dict[str, Any]]] = {
    "productos": [], "inventario": [], "proveedores": [], "pedidos": [], "usuarios": []
}
_counters: Dict[str, int] = {"productos": 0, "inventario": 0, "proveedores": 0, "pedidos": 0, "usuarios": 0}
_lock = threading.Lock()


def use_db() -> bool:
    return bool(DATABASE_URL) and PSYCOPG_OK


def get_conn():
    if not use_db():
        return None
    return psycopg.connect(DATABASE_URL, row_factory=dict_row, autocommit=True)


def next_id(table: str) -> int:
    with _lock:
        _counters[table] = _counters.get(table, 0) + 1
        return _counters[table]


def mem() -> Dict[str, List[Dict[str, Any]]]:
    return _memory


SCHEMA = [
    """CREATE TABLE IF NOT EXISTS proveedores (
        id SERIAL PRIMARY KEY, nombre TEXT NOT NULL, nit TEXT, contacto TEXT,
        email TEXT, telefono TEXT, categoria TEXT, activo BOOLEAN DEFAULT TRUE
    )""",
    """CREATE TABLE IF NOT EXISTS productos (
        id SERIAL PRIMARY KEY, sku TEXT UNIQUE NOT NULL, nombre TEXT NOT NULL,
        categoria TEXT, precio NUMERIC DEFAULT 0, costo NUMERIC DEFAULT 0,
        stock_total INTEGER DEFAULT 0, activo BOOLEAN DEFAULT TRUE
    )""",
    """CREATE TABLE IF NOT EXISTS inventario (
        id SERIAL PRIMARY KEY,
        producto_id INTEGER REFERENCES productos(id) ON DELETE CASCADE,
        bodega TEXT, cantidad INTEGER DEFAULT 0, minimo INTEGER DEFAULT 0,
        ubicacion TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS pedidos (
        id SERIAL PRIMARY KEY,
        proveedor_id INTEGER REFERENCES proveedores(id) ON DELETE SET NULL,
        fecha DATE, estado TEXT DEFAULT 'pendiente', total NUMERIC DEFAULT 0,
        observacion TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
        nombre TEXT, rol TEXT DEFAULT 'usuario'
    )"""
]


def init_schema():
    if not use_db():
        return
    with get_conn() as conn:
        with conn.cursor() as cur:
            for s in SCHEMA:
                cur.execute(s)


SEED_PROVEEDORES = [
    ("Distribuidora Andina SAS", "900123456-1", "Carlos Ramirez", "ventas@andina.co", "+57 301 234 5678", "Abarrotes", True),
    ("Lacteos del Valle Ltda", "800456789-2", "Maria Lopez", "pedidos@lacteosvalle.com", "+57 315 456 7890", "Lacteos", True),
    ("Industrias Aseo Pro", "901789012-3", "Juan Castro", "comercial@aseopro.co", "+57 320 789 0123", "Aseo", True),
    ("Cafe Origen Colombia", "900345678-9", "Ana Restrepo", "ventas@cafeorigen.co", "+57 304 345 6789", "Bebidas", True),
    ("Panaderia La Espiga", "800234567-5", "Pedro Diaz", "contacto@laespiga.co", "+57 310 234 5670", "Panaderia", True),
    ("Snacks Crunch SAS", "901567890-7", "Laura Mejia", "b2b@crunch.co", "+57 318 567 8900", "Snacks", True),
    ("Conservas del Mar", "900876543-2", "Roberto Vega", "ventas@conservasmar.co", "+57 322 876 5432", "Conservas", True),
    ("Importadora Global Foods", "800998877-1", "Sofia Torres", "pedidos@globalfoods.co", "+57 311 998 8771", "General", True)
]

SEED_PRODUCTOS = [
    ("PRD-001", "Arroz Premium 1kg", "Abarrotes", 4500, 3200, 240, True),
    ("PRD-002", "Aceite Girasol 900ml", "Abarrotes", 12500, 9000, 145, True),
    ("PRD-003", "Leche Entera 1L", "Lacteos", 4800, 3500, 320, True),
    ("PRD-004", "Pan Tajado Integral", "Panaderia", 6200, 4500, 95, True),
    ("PRD-005", "Jabon Liquido Lavanda", "Aseo", 18900, 13500, 8, True),
    ("PRD-006", "Cafe Tostado 500g", "Bebidas", 22500, 16000, 65, True),
    ("PRD-007", "Pasta Espagueti 500g", "Abarrotes", 3800, 2500, 180, True),
    ("PRD-008", "Atun en Aceite 170g", "Conservas", 5400, 3800, 220, True),
    ("PRD-009", "Detergente 1kg", "Aseo", 14500, 10200, 12, True),
    ("PRD-010", "Galletas Saladas", "Snacks", 3200, 2100, 410, True)
]

SEED_INVENTARIO = [
    (1, "Bodega Central", 120, 50, "A-01"), (1, "Bodega Norte", 80, 40, "N-03"),
    (2, "Bodega Central", 95, 30, "B-12"), (5, "Bodega Central", 5, 20, "C-08"),
    (9, "Bodega Sur", 8, 25, "S-04"), (3, "Bodega Central", 200, 80, "D-02"),
    (6, "Bodega Norte", 40, 30, "N-15"), (4, "Bodega Central", 60, 35, "P-01"),
    (8, "Bodega Sur", 150, 60, "S-11"), (10, "Bodega Central", 280, 100, "E-07")
]

SEED_PEDIDOS = [
    (1, "2026-05-22", "recibido", 2450000, "Lote completo recibido en bodega central"),
    (3, "2026-05-25", "transito", 1280000, "Llegada estimada 30 mayo"),
    (2, "2026-05-28", "pendiente", 3650000, "Pedido de reposicion semanal"),
    (4, "2026-05-20", "recibido", 1850000, "Calidad premium verificada"),
    (6, "2026-05-29", "pendiente", 920000, "Promocion segundo semestre"),
    (5, "2026-05-27", "transito", 540000, "Producto fresco diario"),
    (7, "2026-05-15", "recibido", 1320000, "Stock para temporada"),
    (8, "2026-05-30", "pendiente", 4850000, "Importacion mensual completa")
]

SEED_USUARIOS = [
    ("admin@e2eflow.com", "admin123", "Gerente Inventario", "admin"),
    ("bodeguero@e2eflow.com", "bod123", "Carlos Bodeguero", "usuario")
]


def seed_if_empty():
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS c FROM proveedores")
                if cur.fetchone()["c"] == 0:
                    cur.executemany("INSERT INTO proveedores (nombre,nit,contacto,email,telefono,categoria,activo) VALUES (%s,%s,%s,%s,%s,%s,%s)", SEED_PROVEEDORES)
                cur.execute("SELECT COUNT(*) AS c FROM productos")
                if cur.fetchone()["c"] == 0:
                    cur.executemany("INSERT INTO productos (sku,nombre,categoria,precio,costo,stock_total,activo) VALUES (%s,%s,%s,%s,%s,%s,%s)", SEED_PRODUCTOS)
                cur.execute("SELECT COUNT(*) AS c FROM inventario")
                if cur.fetchone()["c"] == 0:
                    cur.executemany("INSERT INTO inventario (producto_id,bodega,cantidad,minimo,ubicacion) VALUES (%s,%s,%s,%s,%s)", SEED_INVENTARIO)
                cur.execute("SELECT COUNT(*) AS c FROM pedidos")
                if cur.fetchone()["c"] == 0:
                    cur.executemany("INSERT INTO pedidos (proveedor_id,fecha,estado,total,observacion) VALUES (%s,%s,%s,%s,%s)", SEED_PEDIDOS)
                cur.execute("SELECT COUNT(*) AS c FROM usuarios")
                if cur.fetchone()["c"] == 0:
                    cur.executemany("INSERT INTO usuarios (email,password,nombre,rol) VALUES (%s,%s,%s,%s)", SEED_USUARIOS)
        return

    if not _memory["proveedores"]:
        for n, nit, c, e, t, cat, a in SEED_PROVEEDORES:
            _memory["proveedores"].append({"id": next_id("proveedores"), "nombre": n, "nit": nit, "contacto": c, "email": e, "telefono": t, "categoria": cat, "activo": a})
    if not _memory["productos"]:
        for sku, n, c, p, co, s, a in SEED_PRODUCTOS:
            _memory["productos"].append({"id": next_id("productos"), "sku": sku, "nombre": n, "categoria": c, "precio": p, "costo": co, "stock_total": s, "activo": a})
    if not _memory["inventario"]:
        for pid, b, q, m, u in SEED_INVENTARIO:
            prod = next((x for x in _memory["productos"] if x["id"] == pid), None)
            _memory["inventario"].append({"id": next_id("inventario"), "producto_id": pid, "producto_nombre": prod["nombre"] if prod else "", "bodega": b, "cantidad": q, "minimo": m, "ubicacion": u})
    if not _memory["pedidos"]:
        for pid, f, est, t, ob in SEED_PEDIDOS:
            prov = next((x for x in _memory["proveedores"] if x["id"] == pid), None)
            _memory["pedidos"].append({"id": next_id("pedidos"), "proveedor_id": pid, "proveedor_nombre": prov["nombre"] if prov else "", "fecha": f, "estado": est, "total": t, "observacion": ob})
    if not _memory["usuarios"]:
        for e, p, n, r in SEED_USUARIOS:
            _memory["usuarios"].append({"id": next_id("usuarios"), "email": e, "password": p, "nombre": n, "rol": r})
