import sqlite3

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.db import get_conn
from app.services import catalog

router = APIRouter(prefix="/products", tags=["products"])


class ProductIn(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1)


class ProductOut(ProductIn):
    id: int


@router.post("", status_code=201, response_model=ProductOut)
def create_product(body: ProductIn, conn: sqlite3.Connection = Depends(get_conn)):
    return catalog.create_product(conn, body.sku, body.name)
