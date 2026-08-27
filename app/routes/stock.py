import sqlite3

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.db import get_conn
from app.services import inventory

router = APIRouter(prefix="/stock", tags=["stock"])


class StockIn(BaseModel):
    sku: str
    warehouse: str
    on_hand: int = Field(ge=0)


@router.put("", response_model=StockIn)
def put_stock(body: StockIn, conn: sqlite3.Connection = Depends(get_conn)):
    inventory.set_stock(conn, body.sku, body.warehouse, body.on_hand)
    return body
