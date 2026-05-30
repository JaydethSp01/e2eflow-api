from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class ProductoIn(BaseModel):
    sku: str = Field(..., min_length=1)
    nombre: str = Field(..., min_length=1)
    categoria: str = "General"
    precio: float = 0
    costo: float = 0
    stock_total: int = 0
    activo: bool = True


class ProductoOut(ProductoIn):
    id: int


class InventarioIn(BaseModel):
    producto_id: int
    bodega: str
    cantidad: int = 0
    minimo: int = 0
    ubicacion: str = ""


class InventarioOut(InventarioIn):
    id: int
    producto_nombre: Optional[str] = ""


class ProveedorIn(BaseModel):
    nombre: str = Field(..., min_length=1)
    nit: str = ""
    contacto: str = ""
    email: str = ""
    telefono: str = ""
    categoria: str = "General"
    activo: bool = True


class ProveedorOut(ProveedorIn):
    id: int


class PedidoIn(BaseModel):
    proveedor_id: int
    fecha: str
    estado: str = "pendiente"
    total: float = 0
    observacion: str = ""


class PedidoOut(PedidoIn):
    id: int
    proveedor_nombre: Optional[str] = ""


class LoginIn(BaseModel):
    email: str
    password: str


class LoginOut(BaseModel):
    token: str
    user: dict
