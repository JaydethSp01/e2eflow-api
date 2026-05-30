from fastapi import APIRouter, HTTPException
from typing import List
from app.db import use_db, get_conn, mem, next_id
from app.models import ProductoIn, ProductoOut

router = APIRouter()


@router.get("", response_model=List[ProductoOut])
def list_productos():
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM productos ORDER BY id")
                return cur.fetchall()
    return mem()["productos"]


@router.get("/{pid}", response_model=ProductoOut)
def get_producto(pid: int):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM productos WHERE id=%s", (pid,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, "No encontrado")
                return row
    for p in mem()["productos"]:
        if p["id"] == pid:
            return p
    raise HTTPException(404, "No encontrado")


@router.post("", response_model=ProductoOut)
def create_producto(p: ProductoIn):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO productos (sku,nombre,categoria,precio,costo,stock_total,activo) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                    (p.sku, p.nombre, p.categoria, p.precio, p.costo, p.stock_total, p.activo)
                )
                return cur.fetchone()
    new = {"id": next_id("productos"), **p.model_dump()}
    mem()["productos"].append(new)
    return new


@router.put("/{pid}", response_model=ProductoOut)
def update_producto(pid: int, p: ProductoIn):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE productos SET sku=%s,nombre=%s,categoria=%s,precio=%s,costo=%s,stock_total=%s,activo=%s WHERE id=%s RETURNING *",
                    (p.sku, p.nombre, p.categoria, p.precio, p.costo, p.stock_total, p.activo, pid)
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, "No encontrado")
                return row
    for i, x in enumerate(mem()["productos"]):
        if x["id"] == pid:
            mem()["productos"][i] = {"id": pid, **p.model_dump()}
            return mem()["productos"][i]
    raise HTTPException(404, "No encontrado")


@router.delete("/{pid}")
def delete_producto(pid: int):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM productos WHERE id=%s", (pid,))
        return {"ok": True}
    mem()["productos"] = [x for x in mem()["productos"] if x["id"] != pid]
    return {"ok": True}
