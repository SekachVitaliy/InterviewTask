# Stockroom

Stock reservation service for our warehouses. A shop places a *hold* on items while the
customer checks out. The hold is then either confirmed (stock is deducted), cancelled,
or it expires on its own.

## Running

```bash
poetry install
poetry run pytest
poetry run uvicorn app.main:app --reload   # http://127.0.0.1:8000/docs
```

Data lives in a SQLite file (`stockroom.db`, override with `STOCKROOM_DB`).
Migrations from `migrations/` are applied automatically on startup.

## Domain

| Entity      | Key    | Notes                                                        |
|-------------|--------|--------------------------------------------------------------|
| product     | `sku`  |                                                              |
| warehouse   | `code` |                                                              |
| stock       |        | on-hand quantity of a product in a warehouse                 |
| reservation | `id`   | `held` → `confirmed` or `cancelled`; a hold lasts `ttl_seconds` (default 15 minutes) |

`available = on_hand − sum of held, not yet expired reservations`

## API

| Method | Path                                         | Body                        |
|--------|----------------------------------------------|-----------------------------|
| POST   | `/products`                                  | `{sku, name}`               |
| POST   | `/warehouses`                                | `{code, name}`              |
| PUT    | `/stock`                                     | `{sku, warehouse, on_hand}` |
| GET    | `/products/{sku}/availability?warehouse=MSK` |                             |
| POST   | `/reservations`                              | `{sku, warehouse, qty, ttl_seconds?}` — `ttl_seconds` 60–3600, default 900 |
| GET    | `/reservations/{id}`                         |                             |
| POST   | `/reservations/{id}/confirm`                 |                             |
| POST   | `/reservations/{id}/cancel`                  |                             |

Errors: `404` unknown entity, `409` conflict (duplicate, not enough stock, wrong state), `422` validation.
