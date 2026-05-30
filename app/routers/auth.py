import base64
import json
import time
from fastapi import APIRouter, HTTPException
from app.db import use_db, get_conn, mem
from app.models import LoginIn, LoginOut

router = APIRouter()


def _mock_token(user: dict) -> str:
    payload = {"sub": user["email"], "rol": user.get("rol", "usuario"), "iat": int(time.time())}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


@router.post("/login", response_model=LoginOut)
def login(body: LoginIn):
    user = None
    if use_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id,email,password,nombre,rol FROM usuarios WHERE email=%s", (body.email,))
                user = cur.fetchone()
    else:
        user = next((u for u in mem()["usuarios"] if u["email"] == body.email), None)

    if not user or user["password"] != body.password:
        raise HTTPException(401, "Credenciales invalidas")

    public = {"id": user["id"], "email": user["email"], "nombre": user.get("nombre", ""), "rol": user.get("rol", "usuario")}
    return {"token": _mock_token(public), "user": public}


@router.get("/me")
def me():
    return {"ok": True}
