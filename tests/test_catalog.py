def test_create_product(client):
    r = client.post("/products", json={"sku": "SKU-1", "name": "Widget"})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "sku": "SKU-1", "name": "Widget"}


def test_duplicate_sku_conflicts(client):
    client.post("/products", json={"sku": "SKU-1", "name": "Widget"})
    r = client.post("/products", json={"sku": "SKU-1", "name": "Other"})
    assert r.status_code == 409


def test_create_warehouse(client):
    r = client.post("/warehouses", json={"code": "MSK", "name": "Moscow"})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "code": "MSK", "name": "Moscow"}


def test_duplicate_warehouse_conflicts(client):
    client.post("/warehouses", json={"code": "MSK", "name": "Moscow"})
    assert client.post("/warehouses", json={"code": "MSK", "name": "X"}).status_code == 409
