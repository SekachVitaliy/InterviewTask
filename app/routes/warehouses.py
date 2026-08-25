import sqlite3

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.db import get_conn
from app.services import catalog

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


class WarehouseIn(BaseModel):
    code: str = Field(min_length=1, max_length=16)
    name: str = Field(min_length=1)


class WarehouseOut(WarehouseIn):
    id: int


@router.post("", status_code=201, response_model=WarehouseOut)
def create_warehouse(body: WarehouseIn, conn: sqlite3.Connection = Depends(get_conn)):
    return catalog.create_warehouse(conn, body.code, body.name)
