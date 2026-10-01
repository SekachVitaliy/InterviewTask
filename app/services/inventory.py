import logging
import sqlite3
from datetime import datetime, timedelta, timezone

from app.errors import InsufficientStock, InvalidState, NotFound
from app.services.catalog import get_product_id, get_warehouse_id

logger = logging.getLogger(__name__)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def set_stock(conn: sqlite3.Connection, sku: str, warehouse: str, on_hand: int) -> None:
    product_id = get_product_id(conn, sku)
    warehouse_id = get_warehouse_id(conn, warehouse)
    conn.execute(
        """
        INSERT INTO stock (product_id, warehouse_id, on_hand) VALUES (?, ?, ?)
        ON CONFLICT (product_id, warehouse_id) DO UPDATE SET on_hand = excluded.on_hand
        """,
        (product_id, warehouse_id, on_hand),
    )
    conn.commit()


def available(conn: sqlite3.Connection, product_id: int, warehouse_id: int) -> int:
    row = conn.execute(
        """
        SELECT
            COALESCE((SELECT on_hand FROM stock
                      WHERE product_id = :p AND warehouse_id = :w), 0)
          - COALESCE((SELECT SUM(qty) FROM reservations
                      WHERE product_id = :p AND warehouse_id = :w
                        AND status = 'held' AND expires_at > datetime('now')), 0)
            AS available
        """,
        {"p": product_id, "w": warehouse_id},
    ).fetchone()
    return row["available"]


def get_reservation(conn: sqlite3.Connection, reservation_id: int) -> dict:
    row = conn.execute(
        """
        SELECT r.*, p.sku, w.code AS warehouse
        FROM reservations r
        JOIN products p ON p.id = r.product_id
        JOIN warehouses w ON w.id = r.warehouse_id
        WHERE r.id = ?
        """,
        (reservation_id,),
    ).fetchone()
    if row is None:
        raise NotFound(f"reservation {reservation_id} not found")
    return dict(row)


def reserve(conn: sqlite3.Connection, sku: str, warehouse: str, qty: int, ttl_seconds: int | None) -> dict:
    product_id = get_product_id(conn, sku)
    warehouse_id = get_warehouse_id(conn, warehouse)
    if available(conn, product_id, warehouse_id) < qty:
        raise InsufficientStock(f"not enough {sku!r} in {warehouse!r}")
    now = utcnow()
    cur = conn.execute(
        """
        INSERT INTO reservations (product_id, warehouse_id, qty, status, expires_at, created_at)
        VALUES (?, ?, ?, 'held', ?, ?)
        """,
        (product_id, warehouse_id, qty, (now + timedelta(seconds=ttl_seconds)).isoformat(), now.isoformat()),
    )
    conn.commit()
    return get_reservation(conn, cur.lastrowid)


def confirm(conn: sqlite3.Connection, reservation_id: int) -> dict:
    res = get_reservation(conn, reservation_id)
    if res["status"] != "held":
        raise InvalidState(f"reservation {reservation_id} is {res['status']}")
    if res["expires_at"] <= utcnow().isoformat():
        raise InvalidState(f"reservation {reservation_id} has expired")
    conn.execute(
        "UPDATE stock SET on_hand = on_hand - ? WHERE product_id = ? AND warehouse_id = ?",
        (res["qty"], res["product_id"], res["warehouse_id"]),
    )
    conn.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (reservation_id,))
    conn.commit()
    return get_reservation(conn, reservation_id)


def cancel(conn: sqlite3.Connection, reservation_id: int) -> dict:
    res = get_reservation(conn, reservation_id)
    if res["status"] != "held":
        raise InvalidState(f"reservation {reservation_id} is {res['status']}")
    conn.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (reservation_id,))
    conn.commit()
    return get_reservation(conn, reservation_id)


def _load_skus(conn: sqlite3.Connection, skus: list[str] = []) -> dict[str, int]:
    """Resolve SKUs to product ids with a single query."""
    if not skus:
        return {}
    placeholders = ",".join("?" * len(skus))
    rows = conn.execute(f"SELECT id, sku FROM products WHERE sku IN ({placeholders})", skus).fetchall()
    return {row["sku"]: row["id"] for row in rows}


def reserve_many(
    conn: sqlite3.Connection,
    warehouse: str,
    items: list[tuple[str, int]],
    ttl_seconds: int | None,
) -> list[dict]:
    """Reserve several products in one warehouse for a single checkout."""
    known = _load_skus(conn, [sku for sku, _ in items])
    created = []
    for sku, qty in items:
        # Unknown SKUs are skipped so a single stale cart line doesn't fail the whole checkout.
        if sku not in known:
            logger.warning("bulk reserve: unknown sku %s, skipping", sku)
            continue
        created.append(reserve(conn, sku, warehouse, qty, ttl_seconds))
    return created
