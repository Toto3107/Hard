import time

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from .db import Base, engine
from . import models
from .routers import predict, borewells, auth
from .ml_models import load_models


def init_db_with_retry(max_retries: int = 10, delay_seconds: int = 3):
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            if attempt == max_retries:
                raise
            time.sleep(delay_seconds)


init_db_with_retry()

app = FastAPI(title="RaKsh Backend")


@app.on_event("startup")
def startup_event():
    load_models()


app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(borewells.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
