from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request

from app.db import init_db
from app.routes import render_template

router = APIRouter()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


@router.get("/")
def read_root(request: Request):
    return render_template(request, "home.html")
