from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.routers.auth import get_current_user
from app.models.user import User
from app.services.scraper_service import run_scrape

router = APIRouter(prefix="/api/scrape", tags=["scraper"])

_last_result: dict | None = None
_is_running = False


class ScrapeRequest(BaseModel):
    sources: list[str] | None = None


@router.post("")
async def trigger_scrape(
    body: ScrapeRequest,
    user: User = Depends(get_current_user),
):
    global _last_result, _is_running

    if _is_running:
        raise HTTPException(status_code=409, detail="Ya hay un scraping en ejecucion")

    _is_running = True
    try:
        _last_result = await run_scrape(body.sources)
        return _last_result
    finally:
        _is_running = False


@router.get("/status")
async def scrape_status():
    return {
        "running": _is_running,
        "last_result": _last_result,
    }
