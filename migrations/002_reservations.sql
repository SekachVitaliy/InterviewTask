CREATE TABLE reservations (
    id           INTEGER PRIMARY KEY,
    product_id   INTEGER NOT NULL REFERENCES products (id),
    warehouse_id INTEGER NOT NULL REFERENCES warehouses (id),
    qty          INTEGER NOT NULL CHECK (qty > 0),
    status       TEXT    NOT NULL DEFAULT 'held' CHECK (status IN ('held', 'confirmed', 'cancelled')),
    expires_at   TEXT    NOT NULL,
    created_at   TEXT    NOT NULL
);
