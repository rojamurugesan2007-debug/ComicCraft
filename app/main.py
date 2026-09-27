"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import ROOT_DIR
from app.routes import router
from app.services.files import storage_paths

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

@asynccontextmanager
async def lifespan(_app: FastAPI):
    storage_paths()
    yield

app = FastAPI(title="ComicCraft API", description="Create AI-generated comic stories and printable PDFs.", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(ROOT_DIR / "static")), name="static")
app.include_router(router)
app.mount("/media/panels", StaticFiles(directory=str(storage_paths()[0])), name="panels")
