CREATE TABLE products (
    id   INTEGER PRIMARY KEY,
    sku  TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);

CREATE TABLE warehouses (
    id   INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);

CREATE TABLE stock (
    product_id   INTEGER NOT NULL REFERENCES products (id),
    warehouse_id INTEGER NOT NULL REFERENCES warehouses (id),
    qty_on_hand  INTEGER NOT NULL CHECK (qty_on_hand >= 0),
    PRIMARY KEY (product_id, warehouse_id)
);
