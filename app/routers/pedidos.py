from fastapi import APIRouter, HTTPException
from typing import List
from app.db import use_db, get_conn, mem, next_id
from app.models import PedidoIn, PedidoOut

router = APIRouter()


def _nombre_proveedor(pid: int) -> str:
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT nombre FROM proveedores WHERE id=%s", (pid,))
                r = cur.fetchone()
                return r["nombre"] if r else ""
    p = next((x for x in mem()["proveedores"] if x["id"] == pid), None)
    return p["nombre"] if p else ""


@router.get("", response_model=List[PedidoOut])
def list_pedidos():
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.id, p.proveedor_id, COALESCE(TO_CHAR(p.fecha,'YYYY-MM-DD'),'') AS fecha,
                           p.estado, p.total, p.observacion, pr.nombre AS proveedor_nombre
                    FROM pedidos p LEFT JOIN proveedores pr ON pr.id = p.proveedor_id
                    ORDER BY p.id DESC
                """)
                return cur.fetchall()
    return list(reversed(mem()["pedidos"]))


@router.get("/{pid}", response_model=PedidoOut)
def get_pedido(pid: int):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.id, p.proveedor_id, COALESCE(TO_CHAR(p.fecha,'YYYY-MM-DD'),'') AS fecha,
                           p.estado, p.total, p.observacion, pr.nombre AS proveedor_nombre
                    FROM pedidos p LEFT JOIN proveedores pr ON pr.id=p.proveedor_id WHERE p.id=%s
                """, (pid,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404)
                return row
    for p in mem()["pedidos"]:
        if p["id"] == pid:
            return p
    raise HTTPException(404)


@router.post("", response_model=PedidoOut)
def create_pedido(p: PedidoIn):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO pedidos (proveedor_id,fecha,estado,total,observacion) VALUES (%s,%s,%s,%s,%s) RETURNING id,proveedor_id,TO_CHAR(fecha,'YYYY-MM-DD') AS fecha,estado,total,observacion",
                    (p.proveedor_id, p.fecha, p.estado, p.total, p.observacion)
                )
                row = cur.fetchone()
                row["proveedor_nombre"] = _nombre_proveedor(p.proveedor_id)
                return row
    new = {"id": next_id("pedidos"), **p.model_dump(), "proveedor_nombre": _nombre_proveedor(p.proveedor_id)}
    mem()["pedidos"].append(new)
    return new


@router.put("/{pid}", response_model=PedidoOut)
def update_pedido(pid: int, p: PedidoIn):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE pedidos SET proveedor_id=%s,fecha=%s,estado=%s,total=%s,observacion=%s WHERE id=%s RETURNING id,proveedor_id,TO_CHAR(fecha,'YYYY-MM-DD') AS fecha,estado,total,observacion",
                    (p.proveedor_id, p.fecha, p.estado, p.total, p.observacion, pid)
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404)
                row["proveedor_nombre"] = _nombre_proveedor(p.proveedor_id)
                return row
    for i, x in enumerate(mem()["pedidos"]):
        if x["id"] == pid:
            mem()["pedidos"][i] = {"id": pid, **p.model_dump(), "proveedor_nombre": _nombre_proveedor(p.proveedor_id)}
            return mem()["pedidos"][i]
    raise HTTPException(404)


@router.delete("/{pid}")
def delete_pedido(pid: int):
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM pedidos WHERE id=%s", (pid,))
        return {"ok": True}
    mem()["pedidos"] = [x for x in mem()["pedidos"] if x["id"] != pid]
    return {"ok": True}
