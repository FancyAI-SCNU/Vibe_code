from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import apply_seed_if_needed, engine
from .models import Base
from .routers import action_items as action_items_router
from .routers import notes as notes_router
from .routers import tags as tags_router

app = FastAPI(title="Modern Software Dev Starter (Week 5)")

# Ensure data dir exists
Path("data").mkdir(parents=True, exist_ok=True)

# Mount static frontend - handle both running from week5 and backend directories
frontend_dir = Path("frontend")
if not frontend_dir.exists():
    frontend_dir = Path("../frontend")
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    apply_seed_if_needed()


@app.get("/")
async def root() -> FileResponse:
    index_path = Path("frontend/index.html")
    if not index_path.exists():
        index_path = Path("../frontend/index.html")
    return FileResponse(str(index_path))


# Routers
app.include_router(notes_router.router)
app.include_router(action_items_router.router)
app.include_router(tags_router.router)
