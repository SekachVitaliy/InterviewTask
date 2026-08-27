import sqlite3

from app.services.catalog import get_product_id, get_warehouse_id


def set_stock(conn: sqlite3.Connection, sku: str, warehouse: str, on_hand: int) -> None:
    product_id = get_product_id(conn, sku)
    warehouse_id = get_warehouse_id(conn, warehouse)
    conn.execute(
        """
        INSERT INTO stock (product_id, warehouse_id, qty_on_hand) VALUES (?, ?, ?)
        ON CONFLICT (product_id, warehouse_id) DO UPDATE SET qty_on_hand = excluded.qty_on_hand
        """,
        (product_id, warehouse_id, on_hand),
    )
    conn.commit()


def available(conn: sqlite3.Connection, product_id: int, warehouse_id: int) -> int:
    row = conn.execute(
        "SELECT qty_on_hand FROM stock WHERE product_id = ? AND warehouse_id = ?",
        (product_id, warehouse_id),
    ).fetchone()
    return row["qty_on_hand"] if row else 0
