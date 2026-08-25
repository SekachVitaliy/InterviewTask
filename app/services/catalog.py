import sqlite3

from app.errors import Conflict, NotFound


def create_product(conn: sqlite3.Connection, sku: str, name: str) -> dict:
    try:
        cur = conn.execute("INSERT INTO products (sku, name) VALUES (?, ?)", (sku, name))
    except sqlite3.IntegrityError:
        raise Conflict(f"product {sku!r} already exists")
    conn.commit()
    return {"id": cur.lastrowid, "sku": sku, "name": name}


def create_warehouse(conn: sqlite3.Connection, code: str, name: str) -> dict:
    try:
        cur = conn.execute("INSERT INTO warehouses (code, name) VALUES (?, ?)", (code, name))
    except sqlite3.IntegrityError:
        raise Conflict(f"warehouse {code!r} already exists")
    conn.commit()
    return {"id": cur.lastrowid, "code": code, "name": name}


def get_product_id(conn: sqlite3.Connection, sku: str) -> int:
    row = conn.execute("SELECT id FROM products WHERE sku = ?", (sku,)).fetchone()
    if row is None:
        raise NotFound(f"product {sku!r} not found")
    return row["id"]


def get_warehouse_id(conn: sqlite3.Connection, code: str) -> int:
    row = conn.execute("SELECT id FROM warehouses WHERE code = ?", (code,)).fetchone()
    if row is None:
        raise NotFound(f"warehouse {code!r} not found")
    return row["id"]
