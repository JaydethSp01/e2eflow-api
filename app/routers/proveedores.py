from fastapi import APIRouter, HTTPException
from typing import List
from app.db import use_db, get_conn, mem, next_id
from app.models import ProveedorIn, ProveedorOut

router = APIRouter()


@router.get("", response_model=List[ProveedorOut])
def list_proveedores():
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM proveedores ORDER BY id")
                return cur.fetchall()
    return mem()["proveedores"]


@router.get("/{pid}", response_model=ProveedorOut)
def get_prov(pid: int):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM proveedores WHERE id=%s", (pid,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404)
                return row
    for p in mem()["proveedores"]:
        if p["id"] == pid:
            return p
    raise HTTPException(404)


@router.post("", response_model=ProveedorOut)
def create_prov(p: ProveedorIn):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO proveedores (nombre,nit,contacto,email,telefono,categoria,activo) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                    (p.nombre, p.nit, p.contacto, p.email, p.telefono, p.categoria, p.activo)
                )
                return cur.fetchone()
    new = {"id": next_id("proveedores"), **p.model_dump()}
    mem()["proveedores"].append(new)
    return new


@router.put("/{pid}", response_model=ProveedorOut)
def update_prov(pid: int, p: ProveedorIn):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE proveedores SET nombre=%s,nit=%s,contacto=%s,email=%s,telefono=%s,categoria=%s,activo=%s WHERE id=%s RETURNING *",
                    (p.nombre, p.nit, p.contacto, p.email, p.telefono, p.categoria, p.activo, pid)
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404)
                return row
    for i, x in enumerate(mem()["proveedores"]):
        if x["id"] == pid:
            mem()["proveedores"][i] = {"id": pid, **p.model_dump()}
            return mem()["proveedores"][i]
    raise HTTPException(404)


@router.delete("/{pid}")
def delete_prov(pid: int):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM proveedores WHERE id=%s", (pid,))
        return {"ok": True}
    mem()["proveedores"] = [x for x in mem()["proveedores"] if x["id"] != pid]
    return {"ok": True}
