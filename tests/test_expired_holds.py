"""STOCK-142: products stay "out of stock" after their holds have expired."""
from datetime import timedelta

from app.services.inventory import utcnow


def available(client):
    return client.get("/products/SKU-1/availability", params={"warehouse": "MSK"}).json()["available"]


def test_expired_hold_releases_stock(seeded, conn):
    r = seeded.post("/reservations", json={"sku": "SKU-1", "warehouse": "MSK", "qty": 10, "ttl_seconds": 60})
    rid = r.json()["id"]
    assert available(seeded) == 0

    # fast-forward: the hold expired a second ago
    expired_at = (utcnow() - timedelta(seconds=1)).isoformat()
    conn.execute("UPDATE reservations SET expires_at = ? WHERE id = ?", (expired_at, rid))
    conn.commit()

    assert available(seeded) == 10
