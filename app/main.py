import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routes import router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("comiccraft")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure static directories exist
    Path("static/panels").mkdir(parents=True, exist_ok=True)
    Path("static/exports").mkdir(parents=True, exist_ok=True)
    Path("static/css").mkdir(parents=True, exist_ok=True)
    Path("static/js").mkdir(parents=True, exist_ok=True)
    logger.info("ComicCraft directories verified. Server starting...")
    yield
    logger.info("ComicCraft server shutting down.")


app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Generate personalized comic book storylines, dialogues, and illustrations with Google Gemini models & Stable Diffusion.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for cross-origin frontend interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
Path("static").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include main router
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
