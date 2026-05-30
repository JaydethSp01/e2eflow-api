# E2EFLOW Backend

FastAPI + Postgres (Neon). API REST de gestion de inventarios y pedidos.

## Desarrollo local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

Docs interactivos: http://localhost:8000/docs

## Variables de entorno

- `DATABASE_URL` Connection string de Neon Postgres. Si no esta definida la API arranca en modo memoria con datos seed.
- `CORS_ORIGINS` Lista separada por comas de origenes permitidos (URL de Vercel).
- `PORT` Puerto HTTP (Render lo inyecta automaticamente).

## Endpoints principales

- `GET /health`
- `POST /auth/login`
- `GET|POST /productos`  `GET|PUT|DELETE /productos/{id}`
- `GET|POST /inventario` `GET|PUT|DELETE /inventario/{id}`
- `GET|POST /proveedores` `GET|PUT|DELETE /proveedores/{id}`
- `GET|POST /pedidos` `GET|PUT|DELETE /pedidos/{id}`
- `GET /stats`

## Deploy en Render

1. Tipo: Web Service.
2. Carpeta raiz: `backend/`.
3. Build: Docker (Render detecta el Dockerfile).
4. Variables: `DATABASE_URL` (Neon) y `CORS_ORIGINS` (URL del frontend en Vercel).
5. Health check path: `/health`.

## Usuarios de prueba

- admin@e2eflow.com / admin123 (rol: admin / Gerente)
- bodeguero@e2eflow.com / bod123 (rol: usuario / Bodeguero)
