import sqlite3

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.db import get_conn
from app.services import inventory

router = APIRouter(prefix="/reservations", tags=["reservations"])


class ReservationIn(BaseModel):
    sku: str
    warehouse: str
    qty: int = Field(gt=0)
    ttl_seconds: int | None = Field(default=None, ge=60, le=3600)


class ReservationOut(BaseModel):
    id: int
    sku: str
    warehouse: str
    qty: int
    status: str
    expires_at: str
    created_at: str


class BulkItem(BaseModel):
    sku: str
    qty: int = Field(gt=0)


class BulkReservationIn(BaseModel):
    warehouse: str
    items: list[BulkItem] = Field(min_length=1)
    ttl_seconds: int | None = Field(default=900, ge=60, le=3600)


@router.post("", status_code=201, response_model=ReservationOut)
def create_reservation(body: ReservationIn, conn: sqlite3.Connection = Depends(get_conn)):
    return inventory.reserve(conn, body.sku, body.warehouse, body.qty, body.ttl_seconds)


@router.get("/{reservation_id}", response_model=ReservationOut)
def get_reservation(reservation_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    return inventory.get_reservation(conn, reservation_id)


@router.post("/{reservation_id}/confirm", response_model=ReservationOut)
def confirm_reservation(reservation_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    return inventory.confirm(conn, reservation_id)


@router.post("/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(reservation_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    return inventory.cancel(conn, reservation_id)


@router.post("/bulk", status_code=201, response_model=list[ReservationOut])
def create_bulk_reservations(body: BulkReservationIn, conn: sqlite3.Connection = Depends(get_conn)):
    items = [(item.sku, item.qty) for item in body.items]
    return inventory.reserve_many(conn, body.warehouse, items, body.ttl_seconds)
