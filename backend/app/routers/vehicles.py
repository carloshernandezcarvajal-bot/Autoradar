from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.listing import Listing
from app.models.vehicle import Vehicle
from app.schemas.schemas import ListingOut, ListingWithScore
from app.services.opportunity_score import score_listing
from app.services.analytics import get_price_history

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.get("", response_model=list[ListingOut])
async def list_vehicles(
    brand: str | None = None,
    model: str | None = None,
    year: int | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    conditions = [Listing.is_active == True]
    need_join = False
    if brand:
        conditions.append(Vehicle.brand == brand)
        need_join = True
    if model:
        conditions.append(Vehicle.model == model)
        need_join = True
    if year:
        conditions.append(Vehicle.year == year)
        need_join = True

    if need_join:
        query = select(Listing).join(Vehicle).where(*conditions).options(selectinload(Listing.vehicle))
    else:
        query = select(Listing).where(*conditions).options(selectinload(Listing.vehicle))

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{listing_id}", response_model=ListingWithScore)
async def get_vehicle(listing_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Listing)
        .options(selectinload(Listing.vehicle))
        .where(Listing.id == listing_id)
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")

    score = await score_listing(listing, db)
    return ListingWithScore(
        **{
            "id": listing.id,
            "vehicle_id": listing.vehicle_id,
            "source": listing.source,
            "url": listing.url,
            "current_price": listing.current_price,
            "currency": listing.currency,
            "date_found": listing.date_found,
            "date_updated": listing.date_updated,
            "is_active": listing.is_active,
            "vehicle": listing.vehicle,
            "opportunity_score": score["score"],
            "score_label": score["label"],
        }
    )


@router.get("/{listing_id}/price-history")
async def vehicle_price_history(listing_id: int, db: AsyncSession = Depends(get_db)):
    return await get_price_history(listing_id, db)


@router.get("/brands/list")
async def list_brands(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle.brand).distinct().order_by(Vehicle.brand))
    return [row[0] for row in result.all()]


@router.get("/models/list")
async def list_models(brand: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Vehicle.model).distinct().order_by(Vehicle.model)
    if brand:
        query = query.where(Vehicle.brand == brand)
    result = await db.execute(query)
    return [row[0] for row in result.all()]
