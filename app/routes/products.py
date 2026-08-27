import sqlite3

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.db import get_conn
from app.services import catalog, inventory

router = APIRouter(prefix="/products", tags=["products"])


class ProductIn(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1)


class ProductOut(ProductIn):
    id: int


@router.post("", status_code=201, response_model=ProductOut)
def create_product(body: ProductIn, conn: sqlite3.Connection = Depends(get_conn)):
    return catalog.create_product(conn, body.sku, body.name)


class AvailabilityOut(BaseModel):
    sku: str
    warehouse: str
    available: int


@router.get("/{sku}/availability", response_model=AvailabilityOut)
def get_availability(sku: str, warehouse: str, conn: sqlite3.Connection = Depends(get_conn)):
    product_id = catalog.get_product_id(conn, sku)
    warehouse_id = catalog.get_warehouse_id(conn, warehouse)
    return {"sku": sku, "warehouse": warehouse, "available": inventory.available(conn, product_id, warehouse_id)}
