def reserve(client, qty, ttl_seconds=900):
    return client.post(
        "/reservations",
        json={"sku": "SKU-1", "warehouse": "MSK", "qty": qty, "ttl_seconds": ttl_seconds},
    )


def available(client):
    r = client.get("/products/SKU-1/availability", params={"warehouse": "MSK"})
    return r.json()["available"]


def test_hold_reduces_availability(seeded):
    r = reserve(seeded, 4)
    assert r.status_code == 201
    assert r.json()["status"] == "held"
    assert available(seeded) == 6


def test_cannot_reserve_more_than_available(seeded):
    reserve(seeded, 8)
    assert reserve(seeded, 3).status_code == 409


def test_confirm_deducts_stock(seeded):
    rid = reserve(seeded, 4).json()["id"]
    r = seeded.post(f"/reservations/{rid}/confirm")
    assert r.json()["status"] == "confirmed"
    assert available(seeded) == 6


def test_cancel_releases_stock(seeded):
    rid = reserve(seeded, 4).json()["id"]
    assert seeded.post(f"/reservations/{rid}/cancel").json()["status"] == "cancelled"
    assert available(seeded) == 10


def test_cannot_confirm_cancelled(seeded):
    rid = reserve(seeded, 4).json()["id"]
    seeded.post(f"/reservations/{rid}/cancel")
    assert seeded.post(f"/reservations/{rid}/confirm").status_code == 409


def test_cannot_confirm_expired(seeded, conn):
    rid = reserve(seeded, 4).json()["id"]
    conn.execute("UPDATE reservations SET expires_at = '2025-01-01T00:00:00+00:00' WHERE id = ?", (rid,))
    conn.commit()
    assert seeded.post(f"/reservations/{rid}/confirm").status_code == 409


def test_get_reservation(seeded):
    rid = reserve(seeded, 2).json()["id"]
    body = seeded.get(f"/reservations/{rid}").json()
    assert body["sku"] == "SKU-1" and body["warehouse"] == "MSK" and body["qty"] == 2


def test_unknown_reservation_is_404(seeded):
    assert seeded.get("/reservations/999").status_code == 404


def test_custom_ttl(seeded):
    from datetime import datetime

    body = reserve(seeded, 1, ttl_seconds=120).json()
    delta = datetime.fromisoformat(body["expires_at"]) - datetime.fromisoformat(body["created_at"])
    assert delta.total_seconds() == 120


def test_ttl_out_of_range_rejected(seeded):
    assert reserve(seeded, 1, ttl_seconds=5).status_code == 422
    assert reserve(seeded, 1, ttl_seconds=7200).status_code == 422
