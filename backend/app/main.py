import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import auth, vehicles, search, alerts, favorites, scraper
from app.services.scraper_service import run_scrape

_scrape_task: asyncio.Task | None = None


async def _scheduled_scrape():
    while True:
        try:
            await asyncio.sleep(3600)
            await run_scrape()
        except asyncio.CancelledError:
            break
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scrape_task
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _scrape_task = asyncio.create_task(_scheduled_scrape())
    yield
    if _scrape_task:
        _scrape_task.cancel()
    await engine.dispose()


app = FastAPI(
    title="Autoradar API",
    description="Agregador inteligente de vehiculos usados en Colombia",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(search.router)
app.include_router(alerts.router)
app.include_router(favorites.router)
app.include_router(scraper.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
