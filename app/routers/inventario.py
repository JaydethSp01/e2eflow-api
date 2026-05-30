from fastapi import APIRouter, HTTPException
from typing import List
from app.db import use_db, get_conn, mem, next_id
from app.models import InventarioIn, InventarioOut

router = APIRouter()


@router.get("", response_model=List[InventarioOut])
def list_inventario():
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT i.*, p.nombre AS producto_nombre
                    FROM inventario i LEFT JOIN productos p ON p.id = i.producto_id
                    ORDER BY i.id
                """)
                return cur.fetchall()
    return mem()["inventario"]


@router.get("/{iid}", response_model=InventarioOut)
def get_inv(iid: int):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT i.*, p.nombre AS producto_nombre FROM inventario i LEFT JOIN productos p ON p.id=i.producto_id WHERE i.id=%s""", (iid,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404)
                return row
    for i in mem()["inventario"]:
        if i["id"] == iid:
            return i
    raise HTTPException(404)


def _nombre_producto(pid: int) -> str:
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT nombre FROM productos WHERE id=%s", (pid,))
                r = cur.fetchone()
                return r["nombre"] if r else ""
    p = next((x for x in mem()["productos"] if x["id"] == pid), None)
    return p["nombre"] if p else ""


@router.post("", response_model=InventarioOut)
def create_inv(i: InventarioIn):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO inventario (producto_id,bodega,cantidad,minimo,ubicacion) VALUES (%s,%s,%s,%s,%s) RETURNING *",
                    (i.producto_id, i.bodega, i.cantidad, i.minimo, i.ubicacion)
                )
                row = cur.fetchone()
                row["producto_nombre"] = _nombre_producto(i.producto_id)
                return row
    new = {"id": next_id("inventario"), **i.model_dump(), "producto_nombre": _nombre_producto(i.producto_id)}
    mem()["inventario"].append(new)
    return new


@router.put("/{iid}", response_model=InventarioOut)
def update_inv(iid: int, i: InventarioIn):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE inventario SET producto_id=%s,bodega=%s,cantidad=%s,minimo=%s,ubicacion=%s WHERE id=%s RETURNING *",
                    (i.producto_id, i.bodega, i.cantidad, i.minimo, i.ubicacion, iid)
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404)
                row["producto_nombre"] = _nombre_producto(i.producto_id)
                return row
    for idx, x in enumerate(mem()["inventario"]):
        if x["id"] == iid:
            mem()["inventario"][idx] = {"id": iid, **i.model_dump(), "producto_nombre": _nombre_producto(i.producto_id)}
            return mem()["inventario"][idx]
    raise HTTPException(404)


@router.delete("/{iid}")
def delete_inv(iid: int):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM inventario WHERE id=%s", (iid,))
        return {"ok": True}
    mem()["inventario"] = [x for x in mem()["inventario"] if x["id"] != iid]
    return {"ok": True}
