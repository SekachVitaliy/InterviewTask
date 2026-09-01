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


class ReservationOut(BaseModel):
    id: int
    sku: str
    warehouse: str
    qty: int
    status: str
    expires_at: str
    created_at: str


@router.post("", status_code=201, response_model=ReservationOut)
def create_reservation(body: ReservationIn, conn: sqlite3.Connection = Depends(get_conn)):
    return inventory.reserve(conn, body.sku, body.warehouse, body.qty)


@router.get("/{reservation_id}", response_model=ReservationOut)
def get_reservation(reservation_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    return inventory.get_reservation(conn, reservation_id)


@router.post("/{reservation_id}/confirm", response_model=ReservationOut)
def confirm_reservation(reservation_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    return inventory.confirm(conn, reservation_id)


@router.post("/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(reservation_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    return inventory.cancel(conn, reservation_id)
