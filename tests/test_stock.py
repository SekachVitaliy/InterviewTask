def availability(client, warehouse="MSK"):
    return client.get("/products/SKU-1/availability", params={"warehouse": warehouse})


def test_availability_reflects_stock(seeded):
    assert availability(seeded).json() == {"sku": "SKU-1", "warehouse": "MSK", "available": 10}


def test_put_stock_overwrites(seeded):
    seeded.put("/stock", json={"sku": "SKU-1", "warehouse": "MSK", "on_hand": 3})
    assert availability(seeded).json()["available"] == 3


def test_negative_stock_rejected(seeded):
    r = seeded.put("/stock", json={"sku": "SKU-1", "warehouse": "MSK", "on_hand": -1})
    assert r.status_code == 422


def test_unknown_warehouse_is_404(seeded):
    assert availability(seeded, warehouse="NOPE").status_code == 404


def test_no_stock_row_means_zero(seeded):
    seeded.post("/warehouses", json={"code": "SPB", "name": "Saint Petersburg"})
    assert availability(seeded, warehouse="SPB").json()["available"] == 0
