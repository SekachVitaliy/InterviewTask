import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test.db")
    conn = db.connect(path)
    db.migrate(conn)
    conn.close()
    return path


@pytest.fixture
def conn(db_path):
    conn = db.connect(db_path)
    yield conn
    conn.close()


@pytest.fixture
def client(db_path):
    def override():
        conn = db.connect(db_path)
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[db.get_conn] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def seeded(client):
    client.post("/products", json={"sku": "SKU-1", "name": "Widget"})
    client.post("/warehouses", json={"code": "MSK", "name": "Moscow"})
    client.put("/stock", json={"sku": "SKU-1", "warehouse": "MSK", "on_hand": 10})
    return client
