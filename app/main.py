from contextlib import asynccontextmanager
from enum import Enum
import json
import os
import time
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import CurrentStatus

BASE_DIR = Path(__file__).resolve().parent


class StoryStatus(str, Enum):
    start = "start"
    products = "products"
    purchase = "purchase"


STATUS_IMAGES = {
    StoryStatus.start.value: "/static/images/start.svg",
    StoryStatus.products.value: "/static/images/products.svg",
    StoryStatus.purchase.value: "/static/images/purchase.svg",
}


def read_current_status(db: Session) -> str:
    record = db.scalar(select(CurrentStatus).where(CurrentStatus.id == 1))
    if record is None:
        record = CurrentStatus(id=1, status=StoryStatus.start.value)
        db.add(record)
        db.commit()
        db.refresh(record)
    return record.status


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        read_current_status(db)
    yield


app = FastAPI(
    title="Storytelling Bibivaiafeira",
    description="Página de storytelling controlada por um status persistido.",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/bibivaiafeira", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request):
    with SessionLocal() as db:
        status = read_current_status(db)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"status": status, "image_url": STATUS_IMAGES[status]},
    )


@app.post("/bibivaiafeira")
def update_status(status: StoryStatus = Query(..., description="Novo status: start, products ou purchase")):
    with SessionLocal() as db:
        record = db.get(CurrentStatus, 1)
        if record is None:
            record = CurrentStatus(id=1, status=status.value)
            db.add(record)
        else:
            record.status = status.value
        db.commit()
    return {
        "message": "Status atualizado com sucesso.",
        "status": status.value,
        "image": STATUS_IMAGES[status.value],
    }


@app.get("/api/status")
def get_status():
    with SessionLocal() as db:
        status = read_current_status(db)
    return {"status": status, "image": STATUS_IMAGES[status]}


@app.get("/api/events")
def status_events():
    """SSE: cada conexão consulta o banco e envia eventos somente quando há mudança."""
    def event_stream() -> Iterator[str]:
        previous_status = None
        last_heartbeat = time.monotonic()

        while True:
            with SessionLocal() as db:
                current_status = read_current_status(db)

            if current_status != previous_status:
                payload = json.dumps(
                    {"status": current_status, "image": STATUS_IMAGES[current_status]}
                )
                yield f"event: status\ndata: {payload}\n\n"
                previous_status = current_status
                last_heartbeat = time.monotonic()
            elif time.monotonic() - last_heartbeat >= 15:
                yield ": keep-alive\n\n"
                last_heartbeat = time.monotonic()

            time.sleep(1)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}
