import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_schema, seed_if_empty
from app.routers import productos, inventario, proveedores, pedidos, auth, stats

app = FastAPI(title="E2EFLOW API", version="1.0.0", description="API de gestion de inventarios y pedidos para minoristas")

origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(productos.router, prefix="/productos", tags=["productos"])
app.include_router(inventario.router, prefix="/inventario", tags=["inventario"])
app.include_router(proveedores.router, prefix="/proveedores", tags=["proveedores"])
app.include_router(pedidos.router, prefix="/pedidos", tags=["pedidos"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])


@app.on_event("startup")
def on_startup():
    try:
        init_schema()
        seed_if_empty()
    except Exception as e:
        print(f"[startup] WARN: {e}")


@app.get("/health")
def health():
    return {"status": "ok", "service": "e2eflow-api", "version": "1.0.0"}


@app.get("/")
def root():
    return {"message": "E2EFLOW API", "docs": "/docs", "health": "/health"}
