from fastapi import APIRouter
from app.db import use_db, get_conn, mem

router = APIRouter()


@router.get("")
def stats():
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS c FROM productos")
                total_productos = cur.fetchone()["c"]
                cur.execute("SELECT COUNT(*) AS c FROM proveedores WHERE activo=TRUE")
                total_proveedores = cur.fetchone()["c"]
                cur.execute("SELECT COUNT(*) AS c FROM pedidos WHERE estado IN ('pendiente','transito')")
                total_pedidos = cur.fetchone()["c"]
                cur.execute("SELECT COALESCE(SUM(i.cantidad * p.costo),0) AS v FROM inventario i JOIN productos p ON p.id=i.producto_id")
                valor = float(cur.fetchone()["v"] or 0)
                cur.execute("SELECT COUNT(*) AS c FROM inventario WHERE cantidad <= minimo")
                alertas = cur.fetchone()["c"]
        return {
            "total_productos": total_productos,
            "total_proveedores": total_proveedores,
            "total_pedidos": total_pedidos,
            "valor_inventario": valor,
            "alertas_activas": alertas,
            "rotacion_promedio": 3.4
        }
    m = mem()
    valor = 0.0
    for inv in m["inventario"]:
        prod = next((p for p in m["productos"] if p["id"] == inv["producto_id"]), None)
        if prod:
            valor += float(prod["costo"]) * inv["cantidad"]
    alertas = len([i for i in m["inventario"] if i["cantidad"] <= i["minimo"]])
    return {
        "total_productos": len(m["productos"]),
        "total_proveedores": len([p for p in m["proveedores"] if p["activo"]]),
        "total_pedidos": len([p for p in m["pedidos"] if p["estado"] in ("pendiente", "transito")]),
        "valor_inventario": valor,
        "alertas_activas": alertas,
        "rotacion_promedio": 3.4
    }
