from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import db
from app.errors import Conflict, NotFound
from app.routes import products, reservations, stock, warehouses


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = db.connect()
    db.migrate(conn)
    conn.close()
    yield


app = FastAPI(title="Stockroom", lifespan=lifespan)
app.include_router(products.router)
app.include_router(warehouses.router)
app.include_router(stock.router)
app.include_router(reservations.router)


@app.exception_handler(NotFound)
def not_found(request: Request, exc: NotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(Conflict)
def conflict(request: Request, exc: Conflict) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
